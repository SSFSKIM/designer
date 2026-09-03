# W12 G2 dry run — the lens forms ranked on the native captures (2026-09-03)

Renderer `g2lib.py` (+ `g2_run{,2,3,4,5}.py`, logs `g2_run*.log`, data `g2-dryrun{,2,3,4,5}.json`,
`g2-tau.json`, `g2-body-test.json`). Model Y = a + t·B(q − D⃗(q)), blur-before, B = (1−k)·G_σs(P) +
k·G_10(P) on the raster plate, (σs, k, a, t) from the NATIVE deep interior of each cell and scale
(k fixed at 0.45 on spans ≥ 96 / 0.35 below at pitch 16 where it is unidentifiable; fitted at pitch
32). Self-test: vitrea's own capture rendered under F0 with vitrea's body reads band RMS 0.0052 (1x)
/ 0.0124 (2x) — the renderer reproduces a known lens.

Scores, linear luma: **edge** = band RMS on the straight-edge windows (0.5 < u ≤ 28, ≥ 4 px clear of
the corner arcs — the same pixels for every form); **corner** = mean band RMS over the four (2r+8)-px
corner squares; **SSIM** = whole-crop SSIM of vitrea's current capture with 2 ≤ u ≤ L′+4 replaced by
the model (W11c's dry-run method) — the "now → dry" pair. Fit objective: mean edge RMS over
`rrect-md` + `rrect-ml` at 1x pitch 16 and pitch 32 (corners never in the objective). Lens depth
L = vitrea's `lensDepthPx` (8.0 / 9.18 / 20.8 / 20.8 / 20.8 for sm / capsule / md / ml / lg).

## 1. The forms

| form | what | fitted parameters (md+ml 1x) | fit RMS |
| --- | --- | --- | --- |
| F0 | landed law 1.6·L·(1−u/L)² on n̂_sdf | — | 0.0553 |
| F1 | G·L·(1−u/(E·L))^p on n̂_sdf | G 2.08, E 1.19, p 3.31 | 0.0493 |
| F2m / F2n | F1 profile, pure ellipse direction ê (magnitude / normal fixed) | G 2.14, E 1.39, p 3.99 / 2.10, 1.42, 4.29 | 0.0426 / 0.0455 |
| F2bm / F2bn | F1 profile, direction normalize(n̂ + β·ê) | β 2 / β 1 | 0.0318 / 0.0319 |
| F2t τ | F1 profile, normal fixed, tangential = τ·prof·tanφ_ellipse | τ 0.5: G 2.12, E 1.27, p 3.62 | **0.0320** (τ 0.7: .0339, 0.85: .0386, 1.0: .0455) |
| F3 | F1 + uniform tangential stretch g0·(1−u/Lt)² about the centre | g0 0.25, Lt 18 | 0.0282 — but breaks the small spans (sm 0.060, capsule 0.085 vs F0 0.029 / 0.072) |
| F4n | Apple's terms −min(0.8s,60)·f(u/min(0.25s,20)) + 0.2s·f(u/0.125s), f=(1−x)^p on n̂ | p 2.8 (zero amplitude parameters) | 0.0558 |
| F4-ova0.5-n / -m | F4 (p 2.8), direction normalize(0.5n̂ + 0.5ê) on spans ≥ 96 | — | 0.0436 / 0.0439 |
| F4-ovb-n / -m | F4, direction = ∇(0.5·d_rrect + 0.5·d_oval) | — | 0.0432 / 0.0435 |
| F4-ell-n / -m | F4, pure ellipse direction | — | 0.0544 / 0.0534 |
| F4-ovaBest | F4, ω free | ω 0.6 | 0.0434 |
| F4e | F4 with an extent factor E on both heights, p free | E 1.25, p 3.76 | 0.0549 |
| F4e-ova0.5-n | " + ovalized direction | E 1.25, p 3.79 | 0.0422 |
| F4pp-ova | Apple's terms, separate exponents (p_in, p_out) and E, ovalized | p_in 5.17, p_out 8.0 (bound), E 1.53 | 0.0375 |
| F4+F5 | F4 (p 2.8) + tangential stretch K·q(u)·(p−c)_t/w², q=(1−u/Lt)^m | K 6000, Lt 20.2, m 2.07 | 0.0404 |
| F1+F5 | F1 + the same stretch | K 6380, Lt 21.3, m 2.34 | 0.0273 — breaks the small spans like F3 |
| **F6 ω0.5** | **single power with Apple's span scaling: S = c1·A_in(s), L′ = c2·H_in(s), p; direction ovalized 0.5 on spans ≥ 96, normal fixed** | **c1 0.736, c2 1.313, p 3.61 → S 44.1 / L′ 26.3 (large), 25.9 / 14.4 (capsule), 18.8 / 10.5 (sm)** | **0.0318** |
| F6 ω0 | the same on n̂_sdf | c1 0.72, c2 1.24, p 3.32 | 0.0493 |
| F6 ω free | | ω 0.58 | 0.0313 |

## 2. Scores on every cell (edge / corner / SSIM now → dry)

| cell | F0 | F1 | F2bn | F4n | F4-ova0.5-n | F4pp-ova | **F6 ω0.5** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| md 1x p16 (fit) | .0659 / .0780 / .9537 | .0587 / .0768 / .9593 | .0368 / .0538 / .9688 | .0619 / .0793 / .9575 | .0438 / .0615 / .9653 | .0425 / .0590 / .9664 | **.0366 / .0541 / .9689** |
| ml 1x p16 (fit) | .0520 / .0646 / .9297 | .0473 / .0628 / .9351 | .0351 / .0453 / .9462 | .0532 / .0665 / .9281 | .0473 / .0562 / .9373 | .0405 / .0505 / .9440 | **.0350 / .0454 / .9463** |
| md 1x p32 (fit) | .0488 / .0504 | .0447 / .0460 | .0289 / .0341 | .0497 / .0516 | .0352 / .0431 | .0292 / .0366 | **.0284 / .0342** |
| ml 1x p32 (fit) | .0547 / .0737 | .0465 / .0693 | .0270 / .0353 | .0584 / .0773 | .0479 / .0488 | .0376 / .0391 | **.0273 / .0353** |
| **lg 1x p16 (holdout)** | .0448 / .0496 / .9278 | .0426 / .0490 / .9317 | .0351 / .0398 / .9412 | .0507 / .0536 / .9163 | .0505 / .0527 / .9181 | .0460 / .0490 / .9263 | **.0351 / .0398 / .9414** |
| lg 1x p32 (holdout) | .0512 / .0691 | .0493 / .0665 | .0282 / .0423 | .0687 / .0763 | .0616 / .0659 | .0400 / .0516 | **.0279 / .0424** |
| md 2x (bound .93) | .0742 / .0927 / .9394 | .0688 / .0948 / .9430 | .0414 / .0608 / .9497 | .0714 / .0965 / .9419 | .0482 / .0687 / .9466 | .0472 / .0663 / .9471 | **.0416 / .0614 / .9498** |
| ml 2x | .0586 / .0751 / .9050 | .0543 / .0739 / .9092 | .0384 / .0507 / .9187 | .0606 / .0780 / .9026 | .0532 / .0636 / .9102 | .0446 / .0557 / .9178 | **.0386 / .0509 / .9184** |
| lg 2x (holdout) | .0536 / .0614 / .9065 | .0522 / .0625 / .9104 | .0426 / .0497 / .9174 | .0687 / .0721 / .8928 | .0693 / .0724 / .8926 | .0558 / .0606 / .9059 | **.0428 / .0498 / .9171** |
| sm 1x | .0286 / .0351 / .9977 | .0225 / .0302 / .9979 | .0267 / .0298 / .9980 | .0290 / .0339 / .9973 | (= F4n) | .0253 / .0319 / .9983 | **.0149 / .0267 / .9980** |
| capsule 1x | .0722 / .0948 / .9777 | .0744 / .0955 / .9770 | .0750 / .0965 / .9769 | .0306 / .0376 / .9824 | (= F4n) | .0226 / .0293 / .9848 | **.0126 / .0221 / .9852** |
| sm 2x | .0474 / .0576 / .9967 | .0374 / .0508 / .9969 | .0410 / .0483 / .9968 | .0421 / .0489 / .9962 | (= F4n) | .0388 / .0475 / .9972 | **.0323 / .0442 / .9969** |
| capsule 2x | .0874 / .1073 / .9772 | .0888 / .1076 / .9765 | .0892 / .1088 / .9769 | .0415 / .0488 / .9799 | (= F4n) | .0381 / .0430 / .9818 | **.0304 / .0371 / .9830** |

(F4n/F4-ova on the small spans coincide because ovalization is 0 there. Full tables for every form:
`g2-dryrun{,2,4,5}.json`.)

## 3. Answers

**(1) Direction and the corners.** The corner lobes need the ovalized direction: on md 2x the corner
RMS goes F0 0.093 → F1 0.095 (a better profile alone does nothing for the corner) → F6/F2bn 0.061;
on lg 2x 0.061 → 0.050; md 1x 0.078 → 0.054. By eye (`corner-rrect-md-2x-tl.png`: native | vitrea |
F0 model | best model; `corner-rrect-lg-2x-br.png`, `cell-rrect-md-2x.png`): the best model draws
the pulled lobe with a crisp inner boundary where vitrea draws a soft compression, and the whole-cell
strip reads like the native's lobed band on all four edges. What it still misses at the corner: the
native lobe is a cleaner disc with a dark ring under the bright arc, and the native's *silhouette* is
a continuous (superellipse) corner where ours is circular — visible as the arc's shape in every
corner crop; not modelled here. The corner remains the largest residual (0.05–0.06 against 0.03–0.04
on the straight edges).

Readings of "gradientOvalization 0.5": (a) normalize(0.5n̂ + 0.5ê) and (b) ∇(0.5·d_rrect + 0.5·d_oval)
score the same to 0.0005 and give the same stretch (36.2 / 34.1 / 33.2); (c) ω free lands at 0.58–0.6,
so 0.5 is the pixel-best value within the instrument's resolution. Normal-fixed and magnitude-fixed
differ by ≤ 0.0005 everywhere; normal-fixed keeps the normal component identical across md / ml / lg
by construction, which is what the crossings demand (`g2-dryrun2.json` "invariance": every form's
D_n at x = mid, mid+32, mid+56 for u = 2/3/4/8 — the 'm' forms lose 2–3 px of D_n at x = mid+56 on
md, the 'n' forms none).

**(2) The along-edge period at u = 2.5 (measured 42 / 36.7 / 35.5 on md / ml / lg, 2x).** Ovalized at
0.5: **36.2 / 34.6 / 34.1** (F6) — the right ordering and span trend, about half the measured
stretch. The full ellipse (ω = 1, normal fixed) gives 42.2 / 36.8 / 34.7 — the measured values — but
costs 0.010–0.012 in edge RMS on every large cell (F4-ell-n 0.0544 vs 0.0436; F2t τ 1.0 0.0455 vs
0.0320). A tangential term with its own decay (F5) pinned to the measured stretch at u = 2.5 (K·q(2.5)
= 7936) never beats the ω = 0.5 form on the pixels (best pinned decay: exp(−u/4), fit 0.0474; the
free F4+F5 fit chose K 6000 / Lt 20 / m 2.1 = 38.8 / 35.1 / 33.9, fit 0.0404), and the F5 term breaks
the small spans wherever it is not scaled by the shape (F3 / F1+F5: sm 0.06–0.15). So: the pixels
want half the measured first-lobe stretch; the first-lobe peak reading wants all of it. The pixel
objective is the whole band; the peak reading is one row at u = 2.5. Declared here as a residual
(one row of the band, ≈ 3 px of extra along-edge stretch at the contour on md) rather than fitted.

**(3) Small spans.** Under F1 (vitrea's lens depth) the capsule wants G 2.8 / E 1.5 and sm G 2.2–3.2 /
E 0.8–1.3 against the large spans' 2.1 / 1.2 — the size law's lens part is wrong at the small end
(capsule edge 0.074 at the large-span values, 0.013 at its own). Under Apple's span scaling
(F4/F6: amount ∝ min(0.8·span, 60), height ∝ min(0.25·span, 20)) the small spans fall into place
with **no** per-span parameter: F6's capsule 0.0126 / sm 0.0149 equal the per-cell bests (0.0127 /
0.0147). F4 with p = 3 and zero fitted amplitudes reproduces the crossings on every span to 0.8 px
(large 0.78, capsule 0.78, sm 0.93; p 2.5 → 2.3 / 1.4 / 1.1, p 2 → 4.6 / 3.1 / 2.1, smoothstep → 13 /
9 / 6 — a compact cubic-ish falloff). The lens's size law should therefore be Apple's: magnitude and
extent each linear in the span up to a clamp (60 / 20 at span 75–80), not `sizeThickness`'s smoothstep.

**(4) 2x rows** (dry-run SSIM, native body in the band; the 0.3.0 values 0.9389 / 0.9023 / 0.9013):
F6 predicts **0.9498 / 0.9184 / 0.9171** for md / ml / lg (bound 0.93: md stays met, ml and lg rise
by 0.016 and remain below — their deficit is the 2x interior, `g1-body-2x.md`, not the band). The
nested `glass-over-glass` cell is not rendered here (no simple geometry); its band shares lg's law.
At 1x: md 0.9689, ml 0.9463, lg 0.9414 (holdout, up from 0.9286).

**(5) Worse than the landed law anywhere?** F6: no cell's edge, corner or dry-run SSIM is worse than
F0 beyond noise (sm 1x SSIM 0.9977 → 0.9980; the only "down" is sm 2x SSIM 0.9967 → 0.9969, i.e.
up). F4 with a shared p, F4e and F4pp regress the lg holdout SSIM at 1x (0.9286 → 0.916–0.926) and lg
2x (→ 0.893–0.906) — the two-term profile with Apple's amounts is the wrong *shape* on the pixels
even though it threads the crossings; F1's single steep power (and F6's, its span-scaled twin) is
what the band pixels want. F3 and F1+F5 regress every small span.

**Blur order / band σ (unchanged from G1):** all forms here are blur-before on the native body; the
2x band-vs-interior σ (1.45 vs 3) is not modelled and is why the 2x edge RMS (0.042) stays above
the 1x (0.037) under the same form.

**Photo `rrect-md`:** band RMS vitrea → best model 0.0232 → 0.0166 (1x), 0.0256 → 0.0178 (2x);
whole-crop SSIM unchanged at 0.997–0.998 (the photo's band is low-contrast). Crops
`cell-photo-md-{1,2}x.png`.

## 4. The body test (for G3): Apple's quarter-scale body on `rrect-md`

Y = a + t·[(1−op(u))·T(P) + op(u)·G_σ(T(P))], T = 4×4-device-px box then bilinear tent, σ = 4·r
device px with r = (span+8)/42 = 2.476 (9.9 CSS at 1x, 4.95 at 2x), op(u) = clamp(0.5 + 0.5·(u−1)/
(span/2 − 1), 0.5, 1); (a, t) the only free numbers. Deep interior u > 22:

| scale | Apple body RMS (a, t) | two-component (σs, k) RMS | single σ RMS | deep std native / Apple |
| --- | --- | --- | --- | --- |
| 1x | **0.0322** (0.084, 1.19 — unphysical) | 0.0086 (1.25, 0.45) | 0.0113 (σ 1.25) | 0.102 / 0.097 |
| 2x | **0.0111** (0.383, 0.594) | 0.0104 (3.5, 0.45) | 0.0135 (σ 3.5) | 0.121 / 0.120 |

Per 2-px shell, single-Gaussian (σ CSS px / amplitude), native → Apple model:
1x: u 24: 1.25/0.268 → 1.5/0.331; 32: 1.25/0.244 → 1.5/0.227; 40: 1.25/0.217 → 1.5/0.127; 44:
1.25/0.206 → 2/0.086 — the model's sharp share dies toward the centre three times faster than the
native's. 2x: u 24: 3/0.425 → 2.5/0.398; 32: 3/0.388 → 2.5/0.349; 40: 4/0.496 → 3.5/0.409; 44:
5/0.686 → 3.5/0.395 — the widening with depth is there in kind (2.5 → 3.5) but not in degree (3 → 5),
and the amplitude rise at the centre is absent.

**So: as parametrised it does not explain both scales.** At 2x it is a fair first model (RMS
within 0.001 of the fitted two-component form, σ ≈ 5 CSS at the centre as the impulse reads); at
1x the opacity ramp 0.5 → 1 over span/2 kills the sharp component far faster than the bed shows
(the native keeps amplitude 0.21 at u = 44 against the model's 0.09), and the quarter tent's σ ≈ 1.15
core is right but its share is wrong. Either the ramp's endpoint/values differ from the dump's
working reading at 1x, or the buffer scale is not 0.25 of the *device* scale at 1x. Needs the 2x
probe (and a 1x re-read of the ramp) before a body constant moves.

## 5. Recommendation (ten lines)

1. Declare **F6**: D⃗ = S(span)·(1 − u/L′(span))^p along the ovalized normal, with
   S = 0.736·min(0.8·span, 60) = min(0.589·span, 44.2) CSS px, L′ = 1.313·min(0.25·span, 20) =
   min(0.328·span, 26.3) CSS px, p = 3.6; direction normalize(0.5·n̂_sdf + 0.5·ê) with the normal
   component held at S·prof (so D_n is span-invariant, as the crossings are) on spans ≥ 96, and
   n̂_sdf alone on spans ≤ 44 (Apple's ovalization is 0 there; 56–96 unread — a step at 96 for now).
2. It is the best or equal-best form on every fit cell, the holdout at both scales, the 2x rows
   and both small spans, with three fitted numbers (c1, c2, p) plus Apple's two clamps; nothing regresses.
3. Predicted: 1x checkerboard SSIM md/ml/lg 0.954/0.931/0.929 → 0.969/0.946/0.941; 2x 0.939/0.902/
   0.901 → 0.950/0.918/0.917; capsule 0.977 → 0.985 (1x) / 0.983 (2x); band RMS on the large spans
   −35…−45%, on the capsule −80%.
4. Replace vitrea's lens-depth law for the *lens* (thickness × lensSizeGain, span/2 clamp) with the
   span-linear-with-clamp law above; leave `sizeThickness` to the occlusion/shadow/tone facets.
5. Implement the ovalized direction from the surface's centre and half-extents (two more aux
   channels or an equivalent), blended 0.5 with the field normal, normal component preserved.
6. Keep blur-before and the current body sampling; the 2x band-vs-interior σ is G3's.
7. Residuals to record, not fit: the corner's dark ring and the continuous-corner silhouette;
   ≈ half the measured first-lobe along-edge stretch on md; the 2x interior (G3).
8. Apple's two-term profile with its literal amounts (F4) threads the crossings with zero fitted
   amplitudes but loses on the pixels and on the lg holdout — its *span law* is adopted, its
   *shape* is not; recorded as a finding.
9. The quarter-scale body explains the 2x interior in kind and fails the 1x sharp share — G3 needs
   the 2x probe before any body constant moves.
10. Files: `g2/g2-dryrun.md` (this), `g2-dryrun*.json`, `g2-tau.json`, `g2-body-test.json`, crops
    `corner-rrect-{md,lg}-2x-{tl,br}.png`, `corner-rrect-md-1x-*.png`, `cell-rrect-{md,lg}-2x.png`,
    `cell-rrect-md-1x.png`, `cell-photo-md-{1,2}x.png`.

## 6. Addendum — magnitude-fixed ranking and the ω sweep (after the along-edge measurement)

The coordinator's stretch-aware fit says the lens is one vector field of fixed magnitude whose
direction tilts toward the edge midpoint (normal component 33.0 → 31.5 from the midpoint to 48–60 px
out on md at u = 2; measured tilt tan φ ≈ 0.33–0.40 at 54 px on md, 0.30 at 88 px on lg; per-row
stretch 1.29 / 1.22 / 1.20 / 1.14 / 1.08 / 1.04 / 1.00 at u 1.5 / 2.5 / 4 / 6.5 / 8.5 / 11.5 / 16).
F6 re-fitted (c1, c2, p) at each ω for both readings of the blend and both fixes (`g2-dryrun6.json`,
`g2_run6.log`); "corners" = mean corner RMS over the large cells at both scales:

| form | fit RMS | corners | SSIM md 1x / lg 1x / md 2x / lg 2x | period md/ml/lg 2x | tilt md x+54, u 2 | D_n mid → x+54 | lg tilt @88 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (a) unit-direction blend, m, ω 0.5 | .0318 | .0463 | .9690 / .9412 / .9499 / .9171 | 36.2 / 34.6 / 34.1 | 0.206 | 31.1 → 30.4 | 0.18 |
| (a) m, ω 0.6 | .0312 | .0463 | .9692 / .9412 / .9502 / .9174 | 37.5 / 35.2 / 34.5 | 0.250 | 31.1 → 30.1 | 0.22 |
| (a) m, ω 0.8 | .0349 | .0518 | .9679 / .9400 / .9496 / .9174 | 39.5 / 36.4 / 35.4 | 0.339 | 31.0 → 29.4 | 0.29 |
| (a) m, ω 1.0 | .0426 | .0598 | .9655 / .9385 / .9481 / .9168 | 41.8 / 37.6 / 36.3 | 0.431 | 30.9 → 28.4 | 0.37 |
| (a) n, ω 0.5 | .0318 | .0459 | .9689 / .9414 / .9498 / .9171 | 36.2 / 34.6 / 34.1 | 0.206 | 30.8 → 30.8 | 0.18 |
| (a) n, ω 0.6 | .0313 | .0463 | .9689 / .9410 / .9496 / .9169 | 37.0 / 35.2 / 34.5 | 0.250 | flat | 0.22 |
| **(b) field blend, m, ω 0.6** | **.0294** | **.0446** | **.9698 / .9420 / .9502 / .9175** | 37.2 / 35.1 / 34.5 | 0.237 | 31.1 → 30.3 | 0.21 |
| (b) m, ω 0.7 | .0295 | .0454 | .9697 / .9417 / .9504 / .9178 | 38.2 / 35.8 / 34.9 | 0.282 | 31.1 → 30.0 | 0.25 |
| (b) m, ω 0.8 | .0322 | .0489 | .9687 / .9407 / .9500 / .9176 | 39.2 / 36.4 / 35.4 | 0.330 | 31.1 → 29.5 | 0.29 |
| (b) m, ω 0.5 | .0314 | .0466 | .9688 / .9413 / .9497 / .9171 | 36.2 / 34.6 / 34.0 | 0.193 | 31.1 → 30.5 | 0.17 |
| (b) n, ω 0.6 | .0294 | .0443 | .9697 / .9421 / .9501 / .9175 | 37.0 / 35.1 / 34.4 | 0.237 | flat | 0.21 |
| (b) n, ω 1.0 | .0455 | .0648 | .9630 / .9356 / .9446 / .9131 | 41.5 / 37.8 / 36.4 | 0.431 | flat | 0.37 |

(a) = normalize((1−ω)·n̂ + ω·ê); (b) = ∇((1−ω)·d_rrect + ω·d_oval), d_oval = min(a,b)·(√((x/a)²+(y/b)²) − 1).
Fitted (c1, c2, p) move little across ω: c1 0.73–0.75, c2 1.31–1.48, p 3.6–4.3 (the extent and
exponent grow with ω; at ω 0.6 (b): c1 0.745, c2 1.337, p 3.69 → S 44.7 / L′ 26.7 on the large spans).

**Reading.** (i) Magnitude-fixed and normal-fixed tie (≤ 0.0003) at every ω; the measured normal
drop toward the edge ends (4.5% at 48–60 px) sits between ω 0.6-m (1.6–2.6%) and ω 1.0-m (8%), i.e.
ω ≈ 0.8 by that statistic alone. (ii) The band pixels and the corners both prefer **ω 0.6–0.7** on
the box-inscribed ellipse (fit 0.0294, corners 0.0446); ω 0.8 costs 0.003 / 0.004 and ω 1.0 costs
0.013 / 0.015. (iii) The measured tilt (0.33–0.40 at 54 px on md; 0.30 at 88 px on lg) is what ω
0.8–1.0 produces (0.33–0.43; 0.29–0.37); ω 0.6 gives 0.24 and 0.21 — about 70% of it. (iv) Apple's
`gradientOvalization` 0.5 on the box-inscribed ellipse gives half the measured tilt under either
reading ((a) 0.206, (b) 0.193 at 54 px), so 0.5 does not map to the pixels' 0.6–0.7 or the tilt's
0.8–1.0 as a blend of THIS oval: the oval Apple blends toward is more strongly curved at the edge
midpoint than the ellipse inscribed in the shape's box (by ≈ 1.3–1.6× in b/a² terms), or the
blend is not linear in the unit direction. The corners arbitrate for the *pixels'* value: (b) at
ω 0.6 is the best corner score of every form tried (0.0443–0.0446 against F0's 0.0700).

**Ranking, magnitude-fixed first (fit / corners / lg-1x holdout SSIM):** F6-(b)-m-ω0.6 0.0294 /
0.0446 / 0.9420 ≈ F6-(b)-n-ω0.6 0.0294 / 0.0443 / 0.9421 > F6-(b)-m-ω0.7 0.0295 / 0.0454 / 0.9417 >
F6-(a)-m-ω0.6 0.0312 / 0.0463 / 0.9412 > F6-(a)-ω0.5 (either fix) 0.0318 / 0.046 / 0.9413 > F2bn
0.0319 > F6-(b)-m-ω0.8 0.0322 / 0.0489 / 0.9407 > F4pp-ova 0.0375 > F4-ova0.5 0.0436 > F2m 0.0426 >
F6 ω 1.0 0.0426–0.0455 > F1 0.0493 > F0 0.0553 > F4n 0.0558.

**Declaration candidate, revised:** F6 with the field-blend direction at **ω 0.6**, magnitude fixed
(so the normal component falls ≈ 2% toward the edge ends, as measured in kind), c1 0.745, c2 1.337,
p 3.69: S = min(0.596·span, 44.7), L′ = min(0.334·span, 26.7) CSS px; ω 0 below span 96 (Apple's
value there), unread between 56 and 96. If the parent weights the tilt measurement over the band
pixels, ω 0.8 is the alternative at +0.003 RMS; nothing between 0.5 and 0.8 changes any prediction
in §3 by more than 0.002 SSIM.
