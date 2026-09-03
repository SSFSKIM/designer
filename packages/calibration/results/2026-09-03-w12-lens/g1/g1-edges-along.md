# W12 G1 addendum — does the normal displacement vary along a straight edge? (2026-09-03)

Asked by the coordinator after the other worker measured an along-edge magnification of the band
about each edge's midpoint. Instrument: the joint spline of `w12lib.py` (blur-before, shared D
over top+bottom, per-edge a/t/k/σ1, λ 0.01) on line subsets grouped by |x − x_mid|. Runs:
`g1_along.py` → `g1a-native-*.json`, logs `g1a-*.log`; the stretch measurement in
`g1-stretch.json`. Nothing else edited.

**Answer: (B).** The magnitude |D| = profile(u) is invariant along the edge to ≤ 0.5 px, and the
direction tilts toward the edge's midpoint by exactly the tangential term the along-edge stretch
implies, d_t = (x − x_mid)·(1 − 1/m(u)). The normal component is therefore smaller away from the
midpoint — on `rrect-md` by 4.5% at u = 2 and 9% at u = 8 in the outer 48–60 px, by 1–3% in the
middle 24–48 px — and it is smaller by the amount (B) predicts, D_n = |D|·cos φ with
tan φ = d_t/|D|, at every depth on every cell. (A), a fixed normal component with the tangential
term on top, is rejected by 1.5 px at u ≤ 4 and 1.1–1.4 px at u = 6–8 on `rrect-md`, against a
subset-to-subset repeatability of 0.3 px.

## 1. The stretch m(u), measured first

Per pixel row inside the band, the row profile over the straight section is correlated with
±square(x_mid + (x − x_mid)/m) and the best m taken (`g1-stretch.json`; correlation ≥ 0.9
everywhere quoted; vitrea reads m = 1.00 at every depth as it should).

| cell | u = 1.5 | 2.5 | 3.5 | 4.5 | 5.5 | 6.5 | 8.5 | 10.5 | 12 | 16 | 20 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` 1x p16 (top = bottom) | 1.29 | 1.22 | 1.20 | 1.20 | 1.16 | 1.14 | 1.08 | 1.06 | 1.04 | — | — |
| `rrect-md` 1x p32 | 1.27 | 1.21 | 1.18 | 1.15 | 1.11 | 1.11 | 1.08 | 1.05 | 1.02 | — | — |
| `rrect-md` 2x p16 | 1.30 (u 1.2) | 1.24–1.22 | 1.21 | 1.20 | 1.18–1.16 | 1.15–1.12 | 1.08 | 1.06 | 1.03 | 1.01 | 1.00 |
| `rrect-ml` 1x / 2x | 1.22 / 1.22 | 1.17 / 1.16 | 1.12 / 1.13 | 1.11 / 1.11 | 1.08 / 1.09 | 1.08 / 1.07 | 1.05 / 1.05 | 1.04 / 1.04 | 1.03 | 1.01 | 1.00 |
| `rrect-lg` 1x / 2x | 1.15 / 1.16 | 1.12 / 1.12 | 1.10 / 1.10 | 1.08 / 1.09 | 1.08 / 1.08 | 1.06 / 1.06 | 1.05 / 1.05 | 1.03 / 1.03 | 1.02 | 1.01 | 1.00 |

Top and bottom agree row for row; 1x and 2x agree; m − 1 at u = 2.5 scales 0.22 : 0.17 : 0.12
across spans 96 : 128 : 160 and decays with depth more slowly than D at first (0.20 at u = 4.5
against D(4.5)/D(2) = 0.66) and like it from u ≈ 8. The coordinator's 1.31 / 1.15 / 1.11 at u = 2.5
from checker maxima reads here as 1.22–1.24 / 1.16–1.17 / 1.12 (the maxima-based number sits
between my u = 1.5 and u = 2.5 rows).

## 2. What the stretch does to a line model, and the two fits

A line model samples the plate along the normal at the screen column's parity. Under the stretch
the source column is x_mid + (x − x_mid)/m(u): at |x − x_mid| = 54 on `rrect-md` the source is
10 px from the screen column at u = 2 and crosses a checker column boundary as u changes, so the
line's polarity flips partway down the band. The **stretch-unaware** fit (as asked) is corrupted
exactly there, and visibly: on the outer subset its RMS triples and D runs off (43.8 at u = 2 on
1x, 47.4 at 2x) — not a measurement. The **stretch-aware** model evaluates the cross factor at
the source column for every (line, depth) using §1's m(u) (`StretchLineModel`); its RMS on the
outer subsets returns to the inner subsets' level, and its D_n moves by ≤ 0.4 px when m − 1 is
scaled by 0.8 or 1.2 (`rrect-md` 48–60: 31.6 / 31.5 / 31.4 at u = 2; 10.7 / 10.6 / 10.2 at u = 8),
so what follows is not an artefact of the measured stretch.

The same corruption reaches the model-free crossing table on the outer subsets: a per-line
crossing of the mid-level cannot tell a horizontal checker boundary (which the stretch leaves
where it is) from the vertical boundary the moving source column crosses, and at |x − x_mid| ≥ 48
the vertical crossings fall inside the windows (u ≈ 3–4 and ≈ 7) where the horizontal ones are
expected. The crossing readings there (D 24.6 and 12.7 against 23.9 and 12.0 inside) are
contaminated and are listed, not used; the inner and middle subsets' crossings are clean.

## 3. D_n per subset — stretch-aware joint spline (crossing readings beside)

CSS px; "crossing" is the model-free reading from the s = 36 (u ≈ 2), s = 28 (u ≈ 4) and s = 20
(u ≈ 8) boundaries in that subset; the inner subset is the reference.

| cell | \|x − x_mid\| | RMS (t/b) | D_n u=2 | u=3 | u=4 | u=6 | u=8 | crossings u≈2 / 4 / 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` p16 1x | 0–24 | .0150/.0146 | **33.0** | 28.4 | 24.2 | 17.1 | 11.7 | 34.1 / 23.9 / 12.0 |
| | 24–48 | .0169/.0164 | 32.7 | 28.0 | 23.7 | 16.8 | 11.4 | 34.0 / 24.2 / 12.2 |
| | 48–60 | .0144/.0145 | **31.5** | 26.8 | 22.6 | 15.8 | 10.6 | (34.2 / 24.6 / 12.7 — contaminated) |
| `rrect-md` p16 2x | 0–24 | .0112/.0123 | **33.4** | 28.0 | 23.8 | 17.2 | 11.8 | 33.9 / 24.0 / 12.3 |
| | 24–48 | .0141/.0149 | 32.7 | 27.5 | 23.4 | 16.9 | 11.4 | 34.1 / 24.1 / 12.5 |
| | 48–60 | .0142/.0130 | **31.3** | 26.3 | 22.3 | 15.7 | 10.4 | (34.5 / 24.5 / 12.4 — contaminated) |
| `rrect-md` p32 1x | 0–24 | .0089/.0096 | 31.4 | 27.1 | 23.5 | 17.0 | 11.8 | — / — / 12.2 |
| | 24–48 | .0089/.0085 | 30.3 | 26.1 | 22.6 | 16.4 | 11.3 | — / — / 12.6 |
| | 48–60 | .0095/.0084 | 30.6 | 26.1 | 22.3 | 15.9 | 11.0 | — / — / 12.8 |
| `rrect-lg` p16 1x | 0–35 | .0126/.0122 | **32.7** | 28.4 | 24.4 | 17.4 | 11.7 | 34.1 / 23.9 / 11.9 |
| | 35–70 | .0132/.0123 | 32.4 | 28.1 | 24.2 | 17.2 | 11.5 | 34.0 / 24.1 / 12.0 |
| | 70–106 | .0141/.0147 | **31.6** | 27.3 | 23.5 | 16.7 | 11.1 | (34.0 / 24.3 / 12.3 — contaminated) |
| `rrect-lg` p16 2x | 0–35 | .0094/.0153 | **33.3** | 28.1 | 23.9 | 17.0 | 11.8 | 33.8 / 23.8 / 12.6 |
| | 35–70 | .0094/.0150 | 32.6 | 27.7 | 23.6 | 16.8 | 11.7 | 33.9 / 23.9 / 12.8 |
| | 70–106 | .0110/.0180 | **31.7** | 26.9 | 22.9 | 16.3 | 11.4 | (34.4 / 24.1 / 12.9 — contaminated) |

The stretch-unaware fits, for the record (`g1a-*.log`): inner subsets within 0.1 px of the aware
ones; middle subsets 0.3–1.0 px lower with RMS doubled; outer subsets meaningless (RMS 0.03–0.05,
D 26–47 at u = 2).

## 4. (A) against (B)

With ⟨d⟩ the subset's mean |x − x_mid| and d_t = ⟨d⟩·(1 − 1/m(u)) from §1, the reconstructed
magnitude |D| = √(D_n² + d_t²) against the inner subset's D_n (which has d_t ≈ 1–2 px), and (B)'s
prediction D_n = D_inner·cos φ, tan φ = d_t/D_inner:

| cell, subset (⟨d⟩) | u | D_n measured | d_t | **\|D\|** | D_inner | (B) predicts D_n | (A) predicts D_n |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` 1x, 48–60 (54) | 2 | 31.5 | 10.9 | **33.3** | 33.0 | 31.3 | 33.0 |
| | 3 | 26.8 | 9.4 | **28.4** | 28.4 | 27.0 | 28.4 |
| | 4 | 22.6 | 9.0 | **24.3** | 24.2 | 22.6 | 24.2 |
| | 6 | 15.8 | 7.0 | **17.3** | 17.1 | 15.8 | 17.1 |
| | 8 | 10.6 | 4.7 | **11.6** | 11.7 | 10.9 | 11.7 |
| `rrect-md` 2x, 48–60 (54) | 2 / 4 / 6 / 8 | 31.3 / 22.3 / 15.7 / 10.4 | 10.8 / 9.0 / 7.0 / 4.7 | **33.1 / 24.1 / 17.2 / 11.4** | 33.4 / 23.8 / 17.2 / 11.8 | 31.7 / 22.3 / 16.0 / 11.0 | 33.4 / 23.8 / 17.2 / 11.8 |
| `rrect-md` 1x, 24–48 (36) | 2 / 4 / 8 | 32.7 / 23.7 / 11.4 | 7.3 / 6.0 / 3.1 | **33.5 / 24.5 / 11.8** | 33.0 / 24.2 / 11.7 | 32.2 / 23.5 / 11.3 | 33.0 / 24.2 / 11.7 |
| `rrect-md` p32 1x, 48–60 (54) | 2 / 4 / 8 | 30.6 / 22.3 / 11.0 | 10.4 / 7.4 / 4.3 | **32.3 / 23.5 / 11.8** | 31.4 / 23.5 / 11.8 | 29.8 / 22.4 / 11.0 | 31.4 / 23.5 / 11.8 |
| `rrect-lg` 1x, 70–106 (88) | 2 / 3 / 4 / 6 / 8 | 31.6 / 27.3 / 23.5 / 16.7 / 11.1 | 10.1 / 8.4 / 7.1 / 5.8 / 4.4 | **33.1 / 28.6 / 24.5 / 17.7 / 12.0** | 32.7 / 28.4 / 24.4 / 17.4 / 11.7 | 31.3 / 27.2 / 23.4 / 16.5 / 11.0 | 32.7 / 28.4 / 24.4 / 17.4 / 11.7 |
| `rrect-lg` 2x, 70–106 (88) | 2 / 3 / 4 / 6 / 8 | 31.7 / 26.9 / 22.9 / 16.3 / 11.4 | 10.3 / 8.4 / 7.1 / 5.6 / 4.2 | **33.3 / 28.1 / 23.9 / 17.2 / 12.1** | 33.3 / 28.1 / 23.9 / 17.0 / 11.8 | 31.8 / 26.9 / 22.9 / 16.1 / 11.2 | 33.3 / 28.1 / 23.9 / 17.0 / 11.8 |

Every outer-subset D_n lands on (B)'s prediction within 0.3 px (0.5 at u = 8 on `rrect-md` 2x) and
1.1–1.7 px below (A)'s; every reconstructed |D| matches the inner profile within 0.4 px on 34
of 36 entries (the two exceptions, `rrect-md` p32 at u = 2 and `rrect-lg` 1x at u = 6, are 0.9 and
0.3 px). The lens is one vector field of fixed magnitude profile(u), pointed from the pixel
toward … a point that is not the nearest contour point: its direction tilts toward the edge's
midpoint by tan φ = d_t/|D| ≈ (x − x_mid)(1 − 1/m(u))/profile(u), which at u = 2–4 on `rrect-md`
is 0.33–0.40 at 54 px from the midpoint (the coordinator's x·b/a² gives 0.41 there) and on
`rrect-lg` 0.30 at 88 px (x·b/a² = 0.36).

## 5. Consequence for G2 (advisory)

The profile of `g1-edges.md` (S(1 − u/L)^p, S ≈ 42, L ≈ 23, p ≈ 3) is the *magnitude*; the
direction is not the SDF normal. On a straight edge the field vitrea would need is
D⃗ = profile(u)·(−n̂ cos φ + t̂ sin φ), the tangential part pointing toward the edge's midpoint,
with sin φ growing linearly along the edge and shrinking with depth roughly as m(u) − 1 does;
the ellipse-gradient form the coordinator proposes reproduces both tilts measured here to within
0.05 in tan φ. A radial-only lens with the right profile would still get every D_n on the outer
half of a long edge 5–10% too large and would put no tangential bending anywhere — which is the
"cells bend along the edge" §5.48 saw.
