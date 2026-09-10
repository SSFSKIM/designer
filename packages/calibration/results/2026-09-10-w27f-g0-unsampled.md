# W27f G0 — frozen page-content measurements (2026-09-10)

Numeric rendering of `2026-09-10-w27f-g0-unsampled.json`. No material changed.

`S` = sampled today; `U0` = page content without a hint; `Sh` = sampled with the measured scalar hint; `Uh` = page content at that same hint; `Ch` = CSS page content with that hint; `C` = CSS today; `N` = native.
An overlay in a stack is **always DOM-backed**, including S and Sh. Their labels describe the base. CSS is recorded, not the acceptance target (X1).

Interior L and spread are OKLab mean and population standard deviation, 6 CSS px inside the declared visible footprint. ΔE is mean Euclidean OKLab distance over that footprint. Rim mean is linear luminance on W23’s first two straight-span contour rows; local excess is the W23 two-row integrated excess over adjacent rows. Shadow count is scene-wide, outside all declared shapes, above 1% relative occlusion where backdrop linear luminance ≥0.05. Zero decidable pixels means unmeasurable, not no shadow.

## Headline — the adopter’s unhinted page

The shared declaration supplies the masks. Every GPU report matches its bounds exactly; every CSS report measures a 2 × 2 CSS px size excess from its content-box border. That residual is recorded, not included in the masks. The JSON also preserves the requested-axis provenance checks for all six web configurations. The companion PNG is a qualitative native / S / U0 / Uh contact sheet for four representative scenes.

| Scene | S ΔE | U0 ΔE | U0 − S interior L | Sh ΔE | Uh ΔE | Uh − Sh interior L |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `checkerboard__capsule-button__rest` | 0.02783 | 0.04602 | -0.00184 | 0.07684 | 0.03943 | -0.07438 |
| `checkerboard__capsule-button__rest-tint-orange` | 0.01181 | 0.02119 | -0.00000 | 0.02718 | 0.02129 | -0.01599 |
| `checkerboard__glass-over-glass__rest` | 0.00989 | 0.02329 | -0.00465 | 0.03374 | 0.03279 | -0.06134 |
| `checkerboard__rrect-md__rest` | 0.01236 | 0.03168 | -0.00529 | 0.05196 | 0.03632 | -0.07299 |
| `checkerboard__rrect-ml__rest` | 0.00959 | 0.02283 | -0.00581 | 0.04621 | 0.03313 | -0.07332 |
| `checkerboard__rrect-sm__rest` | 0.02548 | 0.03856 | -0.00003 | 0.07430 | 0.03205 | -0.07675 |
| `checkerboard__toolbar-group__rest` | 0.02680 | 0.04846 | -0.00143 | 0.07529 | 0.04298 | -0.07411 |
| `dark-solid__capsule-button__rest` | 0.00552 | 0.54523 | +0.53977 | 0.00489 | 0.00489 | +0.00000 |
| `dark-solid__capsule-button__rest-tint-orange` | 0.00435 | 0.03888 | -0.03843 | 0.00435 | 0.00416 | +0.00000 |
| `dark-solid__rrect-md__rest` | 0.00877 | 0.00488 | -0.01161 | 0.00877 | 0.07851 | -0.08853 |
| `impulse__capsule-button__rest-tint-orange` | 0.00441 | 0.03909 | -0.03843 | 0.00441 | 0.00436 | +0.00000 |
| `light-solid__capsule-button__rest` | 0.00362 | 0.00181 | -0.00200 | 0.00362 | 0.00153 | -0.00200 |
| `light-solid__capsule-button__rest-tint-orange` | 0.00537 | 0.03787 | -0.03843 | 0.00537 | 0.00540 | +0.00000 |
| `light-solid__rrect-md__rest` | 0.00299 | 0.01028 | +0.01190 | 0.00299 | 0.00349 | -0.00005 |
| `light-solid__rrect-ml__rest` | 0.00213 | 0.01115 | +0.01192 | 0.00213 | 0.00249 | -0.00003 |
| `photo__capsule-button__rest` | 0.02765 | 0.03969 | +0.01747 | 0.03827 | 0.02047 | -0.03260 |
| `photo__capsule-button__rest-tint-blue` | 0.00929 | 0.01483 | +0.00709 | 0.01178 | 0.01020 | -0.00266 |
| `photo__capsule-button__rest-tint-orange` | 0.00815 | 0.01576 | +0.00861 | 0.01185 | 0.00971 | -0.00272 |
| `photo__capsule-button__rest-tint-orange-half` | 0.01804 | 0.02666 | +0.01202 | 0.02521 | 0.01106 | -0.01915 |
| `photo__glass-over-glass__rest` | 0.04260 | 0.02041 | +0.00131 | 0.04337 | 0.03653 | -0.03096 |
| `photo__rrect-md__rest` | 0.04310 | 0.01641 | +0.00281 | 0.04606 | 0.03475 | -0.03587 |
| `photo__rrect-ml__rest` | 0.04574 | 0.01845 | +0.00235 | 0.04758 | 0.03730 | -0.03627 |

## Per term — same declared scene footprint

| Scene | Route | Interior L | Spread | Rim mean | Rim local excess | Shadow / decidable exterior px | ΔE native | Full-paint apparent shade |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `checkerboard__capsule-button__rest` | N | 0.84473 | 0.06350 | 0.70842 | 0.18521 | 5890 / 29564 | 0.00000 | — |
| `checkerboard__capsule-button__rest` | S | 0.87285 | 0.06103 | 0.76026 | 0.18360 | 5958 / 29564 | 0.02783 | — |
| `checkerboard__capsule-button__rest` | U0 | 0.87100 | 0.05770 | 0.75264 | 0.17391 | 5958 / 29564 | 0.04602 | — |
| `checkerboard__capsule-button__rest` | Sh | 0.92375 | 0.04188 | 0.85436 | 0.13674 | 5957 / 29564 | 0.07684 | — |
| `checkerboard__capsule-button__rest` | Uh | 0.84937 | 0.05807 | 0.69593 | 0.16980 | 5958 / 29564 | 0.03943 | — |
| `checkerboard__capsule-button__rest` | C | 0.87479 | 0.06078 | 0.69998 | 0.03891 | 5820 / 29564 | 0.04687 | — |
| `checkerboard__capsule-button__rest` | Ch | 0.92642 | 0.04096 | 0.81570 | 0.02591 | 5820 / 29564 | 0.08336 | — |
| `checkerboard__capsule-button__rest-tint-orange` | N | 0.71670 | 0.01978 | 0.43622 | 0.16912 | 5890 / 29564 | 0.00000 | 0.82868 |
| `checkerboard__capsule-button__rest-tint-orange` | S | 0.72681 | 0.01910 | 0.42612 | 0.12418 | 5958 / 29564 | 0.01181 | 0.85807 |
| `checkerboard__capsule-button__rest-tint-orange` | U0 | 0.72681 | 0.00000 | 0.42539 | 0.12716 | 5958 / 29564 | 0.02119 | 0.85533 |
| `checkerboard__capsule-button__rest-tint-orange` | Sh | 0.74281 | 0.01390 | 0.43615 | 0.09443 | 5958 / 29564 | 0.02718 | 0.91577 |
| `checkerboard__capsule-button__rest-tint-orange` | Uh | 0.72681 | 0.00000 | 0.42539 | 0.12255 | 5958 / 29564 | 0.02129 | 0.85533 |
| `checkerboard__capsule-button__rest-tint-orange` | C | 0.72681 | 0.00000 | 0.37699 | 0.02112 | 5820 / 29564 | 0.02368 | 0.85533 |
| `checkerboard__capsule-button__rest-tint-orange` | Ch | 0.72681 | 0.00000 | 0.37699 | 0.02112 | 5820 / 29564 | 0.02366 | 0.85533 |
| `checkerboard__glass-over-glass__rest` | N | 0.88883 | 0.05429 | 0.86887 | 0.14383 | 11037 / 17950 | 0.00000 | — |
| `checkerboard__glass-over-glass__rest` | S | 0.88439 | 0.05631 | 0.83565 | 0.11247 | 11183 / 17950 | 0.00989 | — |
| `checkerboard__glass-over-glass__rest` | U0 | 0.87974 | 0.04896 | 0.83157 | 0.12085 | 11947 / 17950 | 0.02329 | — |
| `checkerboard__glass-over-glass__rest` | Sh | 0.92309 | 0.04120 | 0.89675 | 0.08445 | 11183 / 17950 | 0.03374 | — |
| `checkerboard__glass-over-glass__rest` | Uh | 0.86175 | 0.05392 | 0.79238 | 0.11104 | 11947 / 17950 | 0.03279 | — |
| `checkerboard__glass-over-glass__rest` | C | 0.88990 | 0.05428 | 0.80914 | 0.02401 | 11130 / 17950 | 0.02105 | — |
| `checkerboard__glass-over-glass__rest` | Ch | 0.92762 | 0.03913 | 0.87885 | 0.01551 | 11130 / 17950 | 0.04051 | — |
| `checkerboard__rrect-md__rest` | N | 0.87639 | 0.04792 | 0.76653 | 0.17521 | 8210 / 24488 | 0.00000 | — |
| `checkerboard__rrect-md__rest` | S | 0.88280 | 0.04453 | 0.77539 | 0.17953 | 8741 / 24488 | 0.01236 | — |
| `checkerboard__rrect-md__rest` | U0 | 0.87751 | 0.03045 | 0.75805 | 0.18118 | 9108 / 24488 | 0.03168 | — |
| `checkerboard__rrect-md__rest` | Sh | 0.92893 | 0.03036 | 0.86571 | 0.14119 | 8741 / 24488 | 0.05196 | — |
| `checkerboard__rrect-md__rest` | Uh | 0.85593 | 0.03064 | 0.71038 | 0.16878 | 9108 / 24488 | 0.03632 | — |
| `checkerboard__rrect-md__rest` | C | 0.88411 | 0.04303 | 0.71509 | 0.03547 | 8458 / 24488 | 0.02960 | — |
| `checkerboard__rrect-md__rest` | Ch | 0.93109 | 0.02891 | 0.82152 | 0.02258 | 8458 / 24488 | 0.05851 | — |
| `checkerboard__rrect-ml__rest` | N | 0.88259 | 0.03549 | 0.77753 | 0.17355 | 11169 / 17976 | 0.00000 | — |
| `checkerboard__rrect-ml__rest` | S | 0.88335 | 0.03897 | 0.77596 | 0.18076 | 11228 / 17976 | 0.00959 | — |
| `checkerboard__rrect-ml__rest` | U0 | 0.87754 | 0.02386 | 0.75728 | 0.18262 | 12030 / 17976 | 0.02283 | — |
| `checkerboard__rrect-ml__rest` | Sh | 0.92928 | 0.02667 | 0.86659 | 0.14328 | 11227 / 17976 | 0.04621 | — |
| `checkerboard__rrect-ml__rest` | Uh | 0.85596 | 0.02401 | 0.70926 | 0.16943 | 12030 / 17976 | 0.03313 | — |
| `checkerboard__rrect-ml__rest` | C | 0.88436 | 0.03675 | 0.71181 | 0.03311 | 11322 / 17976 | 0.01994 | — |
| `checkerboard__rrect-ml__rest` | Ch | 0.92996 | 0.02513 | 0.81652 | 0.02175 | 11322 / 17976 | 0.04958 | — |
| `checkerboard__rrect-sm__rest` | N | 0.84469 | 0.06930 | 0.70910 | 0.18405 | 4186 / 31000 | 0.00000 | — |
| `checkerboard__rrect-sm__rest` | S | 0.87093 | 0.06880 | 0.76028 | 0.18433 | 4202 / 31000 | 0.02548 | — |
| `checkerboard__rrect-sm__rest` | U0 | 0.87090 | 0.06341 | 0.74579 | 0.16849 | 4202 / 31000 | 0.03856 | — |
| `checkerboard__rrect-sm__rest` | Sh | 0.92292 | 0.04661 | 0.85619 | 0.13768 | 4202 / 31000 | 0.07430 | — |
| `checkerboard__rrect-sm__rest` | Uh | 0.84617 | 0.06387 | 0.69252 | 0.15757 | 4202 / 31000 | 0.03205 | — |
| `checkerboard__rrect-sm__rest` | C | 0.87572 | 0.06546 | 0.68127 | 0.00580 | 3765 / 31000 | 0.04382 | — |
| `checkerboard__rrect-sm__rest` | Ch | 0.92797 | 0.04388 | 0.80336 | 0.00259 | 3765 / 31000 | 0.08309 | — |
| `checkerboard__toolbar-group__rest` | N | 0.84466 | 0.06684 | — | — | 7682 / 29708 | 0.00000 | — |
| `checkerboard__toolbar-group__rest` | S | 0.87243 | 0.06302 | — | — | 7690 / 29708 | 0.02680 | — |
| `checkerboard__toolbar-group__rest` | U0 | 0.87100 | 0.05819 | — | — | 7690 / 29708 | 0.04846 | — |
| `checkerboard__toolbar-group__rest` | Sh | 0.92347 | 0.04332 | — | — | 7688 / 29708 | 0.07529 | — |
| `checkerboard__toolbar-group__rest` | Uh | 0.84937 | 0.05856 | — | — | 7690 / 29708 | 0.04298 | — |
| `checkerboard__toolbar-group__rest` | C | 0.87378 | 0.06077 | — | — | 7277 / 29708 | 0.04993 | — |
| `checkerboard__toolbar-group__rest` | Ch | 0.92400 | 0.04045 | — | — | 7277 / 29708 | 0.08195 | — |
| `dark-solid__capsule-button__rest` | N | 0.22254 | 0.00000 | 0.02104 | 0.02006 | 0 / 0 | 0.00000 | — |
| `dark-solid__capsule-button__rest` | S | 0.22728 | 0.00000 | 0.02011 | 0.01680 | 0 / 0 | 0.00552 | — |
| `dark-solid__capsule-button__rest` | U0 | 0.76705 | 0.00000 | 0.59253 | 0.28268 | 0 / 0 | 0.54523 | — |
| `dark-solid__capsule-button__rest` | Sh | 0.22645 | 0.00000 | 0.02002 | 0.01681 | 0 / 0 | 0.00489 | — |
| `dark-solid__capsule-button__rest` | Uh | 0.22645 | 0.00000 | 0.02002 | 0.01681 | 0 / 0 | 0.00489 | — |
| `dark-solid__capsule-button__rest` | C | 0.22728 | 0.00000 | 0.01261 | 0.00181 | 0 / 0 | 0.00863 | — |
| `dark-solid__capsule-button__rest` | Ch | 0.22645 | 0.00000 | 0.01251 | 0.00180 | 0 / 0 | 0.00800 | — |
| `dark-solid__capsule-button__rest-tint-orange` | N | 0.76358 | 0.00000 | 0.48171 | 0.11463 | 0 / 0 | 0.00000 | 0.99879 |
| `dark-solid__capsule-button__rest-tint-orange` | S | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 0 | 0.00435 | 1.00000 |
| `dark-solid__capsule-button__rest-tint-orange` | U0 | 0.72681 | 0.00000 | 0.42539 | 0.12716 | 0 / 0 | 0.03888 | 0.85533 |
| `dark-solid__capsule-button__rest-tint-orange` | Sh | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 0 | 0.00435 | 1.00000 |
| `dark-solid__capsule-button__rest-tint-orange` | Uh | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 0 | 0.00416 | 1.00000 |
| `dark-solid__capsule-button__rest-tint-orange` | C | 0.76524 | 0.00000 | 0.43580 | 0.01651 | 0 / 0 | 0.00639 | 1.00000 |
| `dark-solid__capsule-button__rest-tint-orange` | Ch | 0.76524 | 0.00000 | 0.43580 | 0.01651 | 0 / 0 | 0.00639 | 1.00000 |
| `dark-solid__rrect-md__rest` | N | 0.78290 | 0.00000 | 0.59472 | 0.22995 | 0 / 0 | 0.00000 | — |
| `dark-solid__rrect-md__rest` | S | 0.79134 | 0.00131 | 0.60571 | 0.22939 | 0 / 0 | 0.00877 | — |
| `dark-solid__rrect-md__rest` | U0 | 0.77974 | 0.00000 | 0.61007 | 0.28375 | 0 / 0 | 0.00488 | — |
| `dark-solid__rrect-md__rest` | Sh | 0.79134 | 0.00131 | 0.60571 | 0.22939 | 0 / 0 | 0.00877 | — |
| `dark-solid__rrect-md__rest` | Uh | 0.70282 | 0.00000 | 0.50859 | 0.32308 | 0 / 0 | 0.07851 | — |
| `dark-solid__rrect-md__rest` | C | 0.79436 | 0.00236 | 0.53969 | 0.07423 | 0 / 0 | 0.01278 | — |
| `dark-solid__rrect-md__rest` | Ch | 0.79436 | 0.00236 | 0.53969 | 0.07423 | 0 / 0 | 0.01278 | — |
| `impulse__capsule-button__rest-tint-orange` | N | 0.76358 | 0.00000 | 0.48171 | 0.11463 | 32 / 224 | 0.00000 | 0.99879 |
| `impulse__capsule-button__rest-tint-orange` | S | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 224 | 0.00441 | 1.00000 |
| `impulse__capsule-button__rest-tint-orange` | U0 | 0.72681 | 0.00000 | 0.42539 | 0.12716 | 32 / 224 | 0.03909 | 0.85533 |
| `impulse__capsule-button__rest-tint-orange` | Sh | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 224 | 0.00441 | 1.00000 |
| `impulse__capsule-button__rest-tint-orange` | Uh | 0.76524 | 0.00000 | 0.48531 | 0.11553 | 0 / 224 | 0.00436 | 1.00000 |
| `impulse__capsule-button__rest-tint-orange` | C | 0.76524 | 0.00000 | 0.43580 | 0.01651 | 0 / 224 | 0.00667 | 1.00000 |
| `impulse__capsule-button__rest-tint-orange` | Ch | 0.76524 | 0.00000 | 0.43580 | 0.01651 | 0 / 224 | 0.00667 | 1.00000 |
| `light-solid__capsule-button__rest` | N | 0.98893 | 0.00000 | 0.99587 | 0.05856 | 7827 / 59128 | 0.00000 | — |
| `light-solid__capsule-button__rest` | S | 0.99093 | 0.00098 | 0.97830 | 0.02597 | 8263 / 59128 | 0.00362 | — |
| `light-solid__capsule-button__rest` | U0 | 0.98893 | 0.00000 | 0.96360 | 0.01146 | 11916 / 59128 | 0.00181 | — |
| `light-solid__capsule-button__rest` | Sh | 0.99093 | 0.00098 | 0.97830 | 0.02597 | 8263 / 59128 | 0.00362 | — |
| `light-solid__capsule-button__rest` | Uh | 0.98893 | 0.00000 | 0.96328 | 0.00211 | 8287 / 59128 | 0.00153 | — |
| `light-solid__capsule-button__rest` | C | 0.98893 | 0.00000 | 0.96863 | 0.00406 | 7680 / 59128 | 0.00112 | — |
| `light-solid__capsule-button__rest` | Ch | 0.98893 | 0.00000 | 0.96863 | 0.00406 | 7680 / 59128 | 0.00112 | — |
| `light-solid__capsule-button__rest-tint-orange` | N | 0.76231 | 0.00000 | 0.49359 | 0.14216 | 7860 / 59128 | 0.00000 | 0.99062 |
| `light-solid__capsule-button__rest-tint-orange` | S | 0.76524 | 0.00000 | 0.45031 | 0.05245 | 8296 / 59128 | 0.00537 | 1.00000 |
| `light-solid__capsule-button__rest-tint-orange` | U0 | 0.72681 | 0.00000 | 0.42539 | 0.12716 | 11916 / 59128 | 0.03787 | 0.85533 |
| `light-solid__capsule-button__rest-tint-orange` | Sh | 0.76524 | 0.00000 | 0.45031 | 0.05245 | 8296 / 59128 | 0.00537 | 1.00000 |
| `light-solid__capsule-button__rest-tint-orange` | Uh | 0.76524 | 0.00000 | 0.45031 | 0.05245 | 8296 / 59128 | 0.00540 | 1.00000 |
| `light-solid__capsule-button__rest-tint-orange` | C | 0.76524 | 0.00000 | 0.43077 | 0.00644 | 8040 / 59128 | 0.00766 | 1.00000 |
| `light-solid__capsule-button__rest-tint-orange` | Ch | 0.76524 | 0.00000 | 0.43077 | 0.00644 | 8040 / 59128 | 0.00766 | 1.00000 |
| `light-solid__rrect-md__rest` | N | 0.97803 | 0.00000 | 0.98455 | 0.10024 | 14373 / 48976 | 0.00000 | — |
| `light-solid__rrect-md__rest` | S | 0.97693 | 0.00017 | 0.96141 | 0.07656 | 15690 / 48976 | 0.00299 | — |
| `light-solid__rrect-md__rest` | U0 | 0.98883 | 0.00053 | 0.95812 | 0.01786 | 18216 / 48976 | 0.01028 | — |
| `light-solid__rrect-md__rest` | Sh | 0.97693 | 0.00017 | 0.96141 | 0.07656 | 15690 / 48976 | 0.00299 | — |
| `light-solid__rrect-md__rest` | Uh | 0.97688 | 0.00054 | 0.92813 | 0.00937 | 18216 / 48976 | 0.00349 | — |
| `light-solid__rrect-md__rest` | C | 0.97755 | 0.00000 | 0.93523 | 0.00398 | 14840 / 48976 | 0.00270 | — |
| `light-solid__rrect-md__rest` | Ch | 0.97755 | 0.00000 | 0.93523 | 0.00398 | 14840 / 48976 | 0.00270 | — |
| `light-solid__rrect-ml__rest` | N | 0.97727 | 0.00000 | 0.98362 | 0.10202 | 18420 / 35952 | 0.00000 | — |
| `light-solid__rrect-ml__rest` | S | 0.97694 | 0.00018 | 0.96141 | 0.07656 | 20585 / 35952 | 0.00213 | — |
| `light-solid__rrect-ml__rest` | U0 | 0.98886 | 0.00046 | 0.95813 | 0.01787 | 24060 / 35952 | 0.01115 | — |
| `light-solid__rrect-ml__rest` | Sh | 0.97694 | 0.00018 | 0.96141 | 0.07656 | 20585 / 35952 | 0.00213 | — |
| `light-solid__rrect-ml__rest` | Uh | 0.97691 | 0.00046 | 0.92819 | 0.00951 | 24060 / 35952 | 0.00249 | — |
| `light-solid__rrect-ml__rest` | C | 0.97754 | 0.00006 | 0.93523 | 0.00398 | 20476 / 35952 | 0.00197 | — |
| `light-solid__rrect-ml__rest` | Ch | 0.97754 | 0.00006 | 0.93523 | 0.00398 | 20476 / 35952 | 0.00197 | — |
| `photo__capsule-button__rest` | N | 0.83263 | 0.01177 | 0.64741 | 0.19107 | 12798 / 59101 | 0.00000 | — |
| `photo__capsule-button__rest` | S | 0.84865 | 0.01320 | 0.68760 | 0.20924 | 13053 / 59101 | 0.02765 | — |
| `photo__capsule-button__rest` | U0 | 0.86612 | 0.01449 | 0.71564 | 0.20179 | 13052 / 59101 | 0.03969 | — |
| `photo__capsule-button__rest` | Sh | 0.86173 | 0.01188 | 0.71355 | 0.20127 | 13053 / 59101 | 0.03827 | — |
| `photo__capsule-button__rest` | Uh | 0.82913 | 0.01473 | 0.63789 | 0.20076 | 13052 / 59101 | 0.02047 | — |
| `photo__capsule-button__rest` | C | 0.85319 | 0.00975 | 0.62888 | 0.05456 | 12365 / 59101 | 0.02570 | — |
| `photo__capsule-button__rest` | Ch | 0.86628 | 0.00872 | 0.65821 | 0.05089 | 12365 / 59101 | 0.03628 | — |
| `photo__capsule-button__rest-tint-blue` | N | 0.58005 | 0.00392 | 0.29650 | 0.21791 | 12809 / 59101 | 0.00000 | 0.82251 |
| `photo__capsule-button__rest-tint-blue` | S | 0.58592 | 0.00395 | 0.27279 | 0.16107 | 13075 / 59101 | 0.00929 | 0.82691 |
| `photo__capsule-button__rest-tint-blue` | U0 | 0.59301 | 0.00000 | 0.27344 | 0.14517 | 13076 / 59101 | 0.01483 | 0.85517 |
| `photo__capsule-button__rest-tint-blue` | Sh | 0.58917 | 0.00362 | 0.27275 | 0.15361 | 13076 / 59101 | 0.01178 | 0.84072 |
| `photo__capsule-button__rest-tint-blue` | Uh | 0.58651 | 0.00000 | 0.27208 | 0.15082 | 13076 / 59101 | 0.01020 | 0.83066 |
| `photo__capsule-button__rest-tint-blue` | C | 0.58651 | 0.00000 | 0.22506 | 0.05563 | 12541 / 59101 | 0.01397 | 0.83066 |
| `photo__capsule-button__rest-tint-blue` | Ch | 0.58651 | 0.00000 | 0.22506 | 0.05563 | 12540 / 59101 | 0.01396 | 0.83066 |
| `photo__capsule-button__rest-tint-orange` | N | 0.71160 | 0.00467 | 0.42481 | 0.17223 | 12804 / 59101 | 0.00000 | 0.80962 |
| `photo__capsule-button__rest-tint-orange` | S | 0.71821 | 0.00492 | 0.41878 | 0.14505 | 13066 / 59101 | 0.00815 | 0.82688 |
| `photo__capsule-button__rest-tint-orange` | U0 | 0.72681 | 0.00000 | 0.42539 | 0.12716 | 13069 / 59101 | 0.01576 | 0.85533 |
| `photo__capsule-button__rest-tint-orange` | Sh | 0.72231 | 0.00445 | 0.42174 | 0.13865 | 13067 / 59101 | 0.01185 | 0.84077 |
| `photo__capsule-button__rest-tint-orange` | Uh | 0.71958 | 0.00000 | 0.42183 | 0.14165 | 13068 / 59101 | 0.00971 | 0.83090 |
| `photo__capsule-button__rest-tint-orange` | C | 0.71958 | 0.00000 | 0.36714 | 0.02321 | 12492 / 59101 | 0.01270 | 0.83090 |
| `photo__capsule-button__rest-tint-orange` | Ch | 0.71958 | 0.00000 | 0.36714 | 0.02321 | 12491 / 59101 | 0.01269 | 0.83090 |
| `photo__capsule-button__rest-tint-orange-half` | N | 0.75874 | 0.00739 | 0.51255 | 0.18634 | 12803 / 59101 | 0.00000 | — |
| `photo__capsule-button__rest-tint-orange-half` | S | 0.77150 | 0.00841 | 0.53417 | 0.19273 | 13058 / 59101 | 0.01804 | — |
| `photo__capsule-button__rest-tint-orange-half` | U0 | 0.78352 | 0.00690 | 0.54525 | 0.17126 | 13058 / 59101 | 0.02666 | — |
| `photo__capsule-button__rest-tint-orange-half` | Sh | 0.78001 | 0.00758 | 0.54514 | 0.18262 | 13058 / 59101 | 0.02521 | — |
| `photo__capsule-button__rest-tint-orange-half` | Uh | 0.76086 | 0.00698 | 0.51486 | 0.18755 | 13058 / 59101 | 0.01106 | — |
| `photo__capsule-button__rest-tint-orange-half` | C | 0.77383 | 0.00458 | 0.46870 | 0.03751 | 12401 / 59101 | 0.01877 | — |
| `photo__capsule-button__rest-tint-orange-half` | Ch | 0.78051 | 0.00419 | 0.48045 | 0.03555 | 12391 / 59101 | 0.02419 | — |
| `photo__glass-over-glass__rest` | N | 0.88274 | 0.04683 | 0.84699 | 0.11629 | 20115 / 35873 | 0.00000 | — |
| `photo__glass-over-glass__rest` | S | 0.87356 | 0.04830 | 0.82318 | 0.12228 | 25932 / 35873 | 0.04260 | — |
| `photo__glass-over-glass__rest` | U0 | 0.87488 | 0.05053 | 0.82023 | 0.12527 | 26261 / 35873 | 0.02041 | — |
| `photo__glass-over-glass__rest` | Sh | 0.88275 | 0.04542 | 0.83657 | 0.11615 | 25932 / 35873 | 0.04337 | — |
| `photo__glass-over-glass__rest` | Uh | 0.85180 | 0.05686 | 0.77688 | 0.11791 | 26261 / 35873 | 0.03653 | — |
| `photo__glass-over-glass__rest` | C | 0.87763 | 0.04854 | 0.78662 | 0.03009 | 24453 / 35873 | 0.02775 | — |
| `photo__glass-over-glass__rest` | Ch | 0.88682 | 0.04544 | 0.80270 | 0.02809 | 24451 / 35873 | 0.02952 | — |
| `photo__rrect-md__rest` | N | 0.87207 | 0.01671 | 0.73866 | 0.12694 | 16628 / 48949 | 0.00000 | — |
| `photo__rrect-md__rest` | S | 0.86897 | 0.01513 | 0.74423 | 0.17783 | 20751 / 48949 | 0.04310 | — |
| `photo__rrect-md__rest` | U0 | 0.87178 | 0.02136 | 0.74914 | 0.17936 | 20969 / 48949 | 0.01641 | — |
| `photo__rrect-md__rest` | Sh | 0.88000 | 0.01369 | 0.76600 | 0.17258 | 20751 / 48949 | 0.04606 | — |
| `photo__rrect-md__rest` | Uh | 0.84413 | 0.02156 | 0.69216 | 0.17358 | 20969 / 48949 | 0.03475 | — |
| `photo__rrect-md__rest` | C | 0.86974 | 0.01241 | 0.69004 | 0.04453 | 19686 / 48949 | 0.02586 | — |
| `photo__rrect-md__rest` | Ch | 0.88101 | 0.01136 | 0.71390 | 0.04188 | 19686 / 48949 | 0.03044 | — |
| `photo__rrect-ml__rest` | N | 0.87548 | 0.01845 | 0.75592 | 0.14487 | 20448 / 35925 | 0.00000 | — |
| `photo__rrect-ml__rest` | S | 0.86953 | 0.01743 | 0.75977 | 0.19560 | 25990 / 35925 | 0.04574 | — |
| `photo__rrect-ml__rest` | U0 | 0.87188 | 0.02455 | 0.74382 | 0.18693 | 26361 / 35925 | 0.01845 | — |
| `photo__rrect-ml__rest` | Sh | 0.88054 | 0.01578 | 0.77921 | 0.18657 | 25990 / 35925 | 0.04758 | — |
| `photo__rrect-ml__rest` | Uh | 0.84427 | 0.02479 | 0.68734 | 0.18112 | 26363 / 35925 | 0.03730 | — |
| `photo__rrect-ml__rest` | C | 0.86940 | 0.01363 | 0.68086 | 0.04676 | 24777 / 35925 | 0.02695 | — |
| `photo__rrect-ml__rest` | Ch | 0.88059 | 0.01245 | 0.70514 | 0.04340 | 24777 / 35925 | 0.02987 | — |

## Stack overlay only

The exterior shadow of the overlay cannot be isolated from its base from these composites; only the scene-wide exterior count above is identified. §5.77’s 0.898 was a linear-light prediction; its measured checker/photo GPU readings were 0.8899/0.8739, CSS 0.8435/0.8166. The masks and current material differ, so the older numbers remain beside these, not rewritten.

| Scene | Route | Interior linear Y | Interior OKLab L | Spread | Rim mean | Rim local excess | ΔE native |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `checkerboard__glass-over-glass__rest` | N | 0.904655 | 0.967141 | 0.002773 | 0.960679 | 0.111642 | 0.000000 |
| `checkerboard__glass-over-glass__rest` | S | 0.890113 | 0.961914 | 0.004928 | 0.897061 | 0.042743 | 0.007735 |
| `checkerboard__glass-over-glass__rest` | U0 | 0.884637 | 0.959951 | 0.003287 | 0.907361 | 0.058576 | 0.008603 |
| `checkerboard__glass-over-glass__rest` | Sh | 0.931619 | 0.976651 | 0.003569 | 0.928957 | 0.024549 | 0.009216 |
| `checkerboard__glass-over-glass__rest` | Uh | 0.866897 | 0.953494 | 0.003459 | 0.876420 | 0.051131 | 0.015833 |
| `checkerboard__glass-over-glass__rest` | C | 0.901282 | 0.965922 | 0.004954 | 0.906267 | 0.011117 | 0.004904 |
| `checkerboard__glass-over-glass__rest` | Ch | 0.939657 | 0.979448 | 0.004324 | 0.942332 | 0.006629 | 0.011961 |
| `photo__glass-over-glass__rest` | N | 0.893533 | 0.964243 | 0.002174 | 0.938737 | 0.084228 | 0.000000 |
| `photo__glass-over-glass__rest` | S | 0.873339 | 0.956292 | 0.002776 | 0.888001 | 0.047788 | 0.019478 |
| `photo__glass-over-glass__rest` | U0 | 0.872080 | 0.956285 | 0.003711 | 0.898521 | 0.062044 | 0.012283 |
| `photo__glass-over-glass__rest` | Sh | 0.883516 | 0.959945 | 0.002574 | 0.895282 | 0.044071 | 0.018781 |
| `photo__glass-over-glass__rest` | Uh | 0.849239 | 0.947975 | 0.003620 | 0.868225 | 0.053255 | 0.020678 |
| `photo__glass-over-glass__rest` | C | 0.885039 | 0.960698 | 0.001855 | 0.894201 | 0.011367 | 0.013414 |
| `photo__glass-over-glass__rest` | Ch | 0.894362 | 0.964002 | 0.001767 | 0.902291 | 0.010772 | 0.013611 |
