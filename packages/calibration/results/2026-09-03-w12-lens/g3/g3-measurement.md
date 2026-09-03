# W12 G3 — the 2x probe measured on its pitch axis

**What this is.** The measurement Decision Log 5 of
`docs/doperpowers/specs/2026-09-03-w12-lens-band-structure.md` names, run on the two probe beds and
nothing else: the 1x W9 probe (`results/2026-09-02-w9-probe/`, claims §5.31) and the 2x W12 probe
(`results/2026-09-03-w12-lens/probe-2x/`, claims §5.53), 56 cells each, the same scene set at the two
scales. Nothing here is captured, nothing is fitted into the product, and no constant under
`packages/` is touched. The declaration is the orchestrator's and the user's; this document is the
numbers it should be written from.

**Instrument, and its checks.** Every reading is taken by `g3lib.py` on one code path, the 2x probe
and the 1x probe alike, so each 2x number carries the 1x number from the same code beside it. Four
published readings are reproduced before anything new is claimed:

| check | published | measured here |
| --- | --- | --- |
| §5.41 §1, 1x pitch-16 single Gaussian, σ / t by span | 1.25 / 0.340, 1.25 / 0.331, 1.25 / 0.246, 1.25 / 0.165, 1.00 / 0.093 | identical to three decimals on all five spans (`check_5_41_1`, every row `matches: true`) |
| §5.38 §3, 1x heavy share at spans 96 / 128 / 160 (σ_sharp fixed at 1, joint over five pitches) | 0.56 / 0.66 / 0.76 | **0.555 / 0.662 / 0.764**, with σ_heavy 8 / 9 / 9 and a 0.416 / 0.438 / 0.464 |
| §5.49 §7, 2x `rrect-md` pitch 16 | σ 3.0 CSS px, t 0.413, level 0.473 | **σ 3.00, t 0.413, a 0.473** |
| §5.49 §2, model-free crossings on `rrect-md` (D at u ≈ 2 / 3 / 4 / 8 / 20) | 1x 34.2 / 29.1 / 24.0 / 12.1 / 0.2; 2x 33.7 / 29.2 / 24.0 / 12.4 / −0.3 | 1x **34.08 / 29.08 / 24.05 / 12.10 / 0.14**; 2x **33.97 / 29.17 / 24.10 / 12.36 / −0.24** |

The plate generator is checked against the committed rasters at both scales before it is used: every
checkerboard family and the `lc16` twin agree to 0.0 (`plate_verification`), so the analytic plate is
the raster.

**Headline.** The reference's body kernel is **one kernel in device pixels at both scales** — a
flat-topped core exactly the width of the quarter-device-scale buffer's pixel (4 device px) on a base
of σ ≈ 9–10 **device** px — and the only thing the second scale changes is **how much of the
unblurred core leaks through**: at 2x the sharp term is roughly 0.4 of the mixing weight weaker at
every span and dies by mid-depth instead of surviving to the centre. A two-component law whose heavy
σ is fixed in device px and whose share law carries one scale term fits both probes at once
(RMS 0.0179 on the fit set, 0.0197 on the untouched `rrect-lg` holdout) — the same residual §5.41
reached at 1x alone, now across both beds. The landed law reaches 0.0164 at 1x and 0.0464 at 2x.

---

## 1. The interior, per scale × span × pitch

The 5.41 inset interior box (inset `min(max(radius, 12), h/2 − 8)` CSS px), linear luminance, over
the backdrop plate. A `*` marks a row where the fit sits at the identifiability ceiling — the largest
σ whose blurred plate still carries 5% of the plate's own contrast under that box — or where the
plate is uniform under the box (`rrect-sm` at pitch 64) or the reference is flattened; those σ and t
are not measurements of a width, they are the statement that no width is identifiable there.

### Table 1a — single Gaussian, σ in CSS px (device px in brackets), and t

| cell | p4 1x | p4 2x | p8 1x | p8 2x | p16 1x | p16 2x | p32 1x | p32 2x | p64 1x | p64 2x | lc16 1x | lc16 2x |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sm 32 | 2.00 (2.0) t +1.494* | 0.75 (1.5) t +0.297 | 1.50 (1.5) t +0.413 | 0.75 (1.5) t +0.215 | 1.25 (1.2) t +0.340 | 1.25 (2.5) t +0.367 | 1.50 (1.5) t +0.408 | 1.75 (3.5) t +0.445 | 8.00 (8.0) t +0.197* | 5.00 (10.0) t +0.125* | 1.25 (1.2) t +0.263 | 1.25 (2.5) t +0.146 |
| cap 44 | 2.00 (2.0) t +1.493* | 0.75 (1.5) t +0.288 | 1.50 (1.5) t +0.410 | 0.75 (1.5) t +0.203 | 1.25 (1.2) t +0.331 | 1.50 (3.0) t +0.376 | 1.50 (1.5) t +0.398 | 1.75 (3.5) t +0.434 | 2.00 (2.0) t +0.408 | 2.50 (5.0) t +0.472 | 1.25 (1.2) t +0.255 | 1.25 (2.5) t +0.278 |
| md 96 | 2.00 (2.0) t +1.168* | 1.25 (2.5) t +0.290 | 1.50 (1.5) t +0.340 | 0.50 (1.0) t +0.033 | 1.25 (1.2) t +0.246 | 3.00 (6.0) t +0.413 | 2.50 (2.5) t +0.404 | 3.50 (7.0) t +0.505 | 3.50 (3.5) t +0.481 | 3.50 (7.0) t +0.511 | 1.25 (1.2) t +0.179 | 3.50 (7.0) t +0.348 |
| ml 128 | 2.00 (2.0) t +0.836* | 2.00 (4.0) t +0.619* | 1.75 (1.8) t +0.299 | 1.50 (3.0) t −0.055 | 1.25 (1.2) t +0.165 | 8.00 (16.0) t +2.523* | 3.00 (3.0) t +0.355 | 4.00 (8.0) t +0.448 | 4.00 (4.0) t +0.442 | 4.00 (8.0) t +0.468 | 1.25 (1.2) t +0.113 | 8.00 (16.0) t +1.771* |
| lg 160 | 2.00 (2.0) t +0.565* | 2.00 (4.0) t +0.378* | 1.75 (1.8) t +0.223 | 1.50 (3.0) t −0.044 | 1.00 (1.0) t +0.093 | 8.00 (16.0) t +1.572* | 4.00 (4.0) t +0.328 | 5.00 (10.0) t +0.388 | 5.00 (5.0) t +0.410 | 5.00 (10.0) t +0.420 | 1.00 (1.0) t +0.059 | 8.00 (16.0) t +1.029* |

### Table 1b — two components, σ_sharp / σ_heavy (CSS px) and the heavy share k

| cell | p4 1x | p4 2x | p8 1x | p8 2x | p16 1x | p16 2x | p32 1x | p32 2x | p64 1x | p64 2x | lc16 1x | lc16 2x |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sm 32 | — | — | 1.50/3.0 k 0.00 | 0.50/3.0 k 0.26 | 1.25/3.0 k 0.01 | 0.75/8.0 k 0.86 | 1.25/10.0 k 0.38 | 0.75/5.0 k 0.51 | 6.00/8.0 k 1.00 | 5.00/14.0 k 0.00 | 1.25/3.0 k 0.02 | 0.50/5.0 k 0.67 |
| cap 44 | — | — | 1.50/4.0 k 0.00 | 0.50/3.0 k 0.25 | 1.25/3.0 k 0.00 | 0.75/8.0 k 0.87 | 1.25/10.0 k 0.39 | 0.75/5.0 k 0.54 | 1.50/10.0 k 0.28 | 0.75/5.0 k 0.51 | 1.25/3.0 k 0.02 | 0.75/8.0 k 0.87 |
| md 96 | — | — | 1.50/3.0 k 0.19 | 0.50/3.0 k 0.00 | 1.25/3.0 k 0.00 | 0.50/8.0 k 0.98 | 1.25/10.0 k 0.58 | 0.50/4.0 k 0.90 | 1.25/8.0 k 0.49 | 0.50/4.0 k 0.85 | 1.25/4.0 k 0.00 | 0.50/8.0 k 0.98 |
| ml 128 | — | — | 1.50/3.0 k 0.48 | — | 1.25/3.0 k 0.00 | 0.75/8.0 k 1.00 | 1.25/16.0 k 0.90 | 4.00/6.0 k 0.21 | 1.50/9.0 k 0.54 | 4.00/18.0 k 0.07 | 1.25/7.0 k 0.00 | 0.25/8.0 k 1.00 |
| lg 160 | — | — | 1.75/4.0 k 0.00 | — | 1.00/6.0 k 0.00 | 5.00/8.0 k 1.00 | 1.25/12.0 k 0.84 | 3.50/5.0 k 0.86 | 1.50/9.0 k 0.66 | 4.00/11.0 k 0.31 | 1.00/6.0 k 0.00 | 1.75/8.0 k 1.00 |

**Reading.** Per cell in isolation the two-component decomposition is under-determined — one pitch
sees at most one of the two widths — which is exactly why §5.41 fitted jointly over pitches and why
the joint fits in §3 and §6 below are the load-bearing ones. What the per-cell table does say is
where the two scales part company. At the pitches where both scales resolve structure (16 / 32 / 64
on spans ≥ 96) the 2x σ in **CSS** px is 1.4–3× the 1x one, but in **device** px the two are within
about 30% of each other on `rrect-md` (2.5 → 6.0, 2.5 → 7.0, 3.5 → 7.0) and equal on `rrect-lg` at
pitch 64 (5.0 → 10.0 device). The 2x transmission is higher at every span and pitch that resolves
(md p32 0.404 → 0.505, lg p32 0.328 → 0.388), and the fine pitches invert: at pitch 8 the 1x
reference still passes t 0.22–0.41 while the 2x reference passes 0.03 or nothing at all on spans
≥ 96. A finer core with a much weaker weight is the shape of that.

The `lc16` twin (same pitch, same linear mean (0.4997 against 0.5000), 57% of the contrast) tracks pitch 16 at both scales:
its t is 0.63–0.77 of pitch 16's at 1x (falling with span) and 0.40–0.84 at 2x, at the same σ, so the response is close
to linear in backdrop contrast and the pitch-16 reading is not an artefact of the black/white plate.

**Noise bar on the frequency-settled cells** (§5.53 §2 — three `rrect-sm` cells at 2x hold a second
settled state; the two states measured here in the same quantities):

| cell | state distance, interior RMS | interior mean Δ | Δσ | Δt |
| --- | --- | --- | --- | --- |
| `checkerboard-8__rrect-sm` | 0.237 | −0.234 | 0.00 | +0.097 |
| `checkerboard-lc16__rrect-sm` | 0.100 | +0.095 | 0.00 | −0.137 |
| `checkerboard-64__rrect-sm` | 0.0093 | −0.0092 | (plate uniform under the box) | — |
| `light-solid__rrect-sm` (noise, §5.53) | 0.0006 | −0.0006 | — | — |

On those three rows a residual below ≈ 0.1–0.24 of linear luminance is bounded by the material's own
two states before it is bounded by any law. No `rrect-md`, `-ml` or `-lg` cell is affected, and the
holdout is unanimous on every backdrop at 2x.

---

## 2. Depth

Bands are annuli of the silhouette's own distance field, 8 CSS px wide, from u = 20 (outside the
lens: §5.49 §2 puts D < 1 px from u ≈ 17–18 at every span) to the half-span. The single-Gaussian
(σ, t) is the primary statistic because at pitch 8 and 16 the heavy component is annihilated and only
one component is identifiable; where both are identifiable the two-component numbers are in
`g3-measurement.json` under `depth`.

### Table 2a — pitch 16

| cell | u 20–28 | u 28–36 | u 36–44 | u 44–52 | u 52–60 | u 60–68 | u 68–76 | u 76–80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lg 1x | σ 1.25 t +0.169 | σ 1.25 t +0.148 | σ 1.25 t +0.128 | σ 1.00 t +0.105 | σ 1.00 t +0.088 | σ 1.00 t +0.072 | σ 1.00 t +0.054 | σ 0.75 t +0.040 |
| lg 2x | σ 8.00 t +2.587 | σ 8.00 t +2.268 | σ 8.00 t +2.007 | σ 8.00 t +1.717 | σ 8.00 t +1.483 | σ 8.00 t +1.222 | σ 8.00 t +1.004 | σ 8.00 t +0.834 |
| md 1x | σ 1.25 t +0.270 | σ 1.25 t +0.246 | σ 1.25 t +0.218 | σ 1.25 t +0.204 | | | | |
| md 2x | σ 3.00 t +0.438 | σ 3.00 t +0.411 | σ 4.00 t +0.511 | σ 8.00 t +3.095 | | | | |
| ml 1x | σ 1.25 t +0.216 | σ 1.25 t +0.196 | σ 1.25 t +0.171 | σ 1.25 t +0.153 | σ 1.25 t +0.130 | σ 1.00 t +0.111 | | |
| ml 2x | σ 3.50 t +0.424 | σ 5.00 t +0.652 | σ 8.00 t +2.686 | σ 8.00 t +2.335 | σ 8.00 t +2.055 | σ 8.00 t +1.823 | | |

(The 2x rows that read σ 8.00 with t > 1 are at the identifiability ceiling: the 2x reference retains
no pitch-16 structure that deep, so the regression is fitting the plate's residual gradient. They are
"no structure", not "a wide blur".)

### Table 2b — pitch 32

| cell | u 20–28 | u 28–36 | u 36–44 | u 44–52 | u 52–60 | u 60–68 | u 68–76 | u 76–80 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lg 1x | σ 3.00 t +0.344 | σ 3.50 t +0.348 | σ 3.50 t +0.329 | σ 2.50 t +0.258 | σ 5.00 t +0.361 | σ 5.00 t +0.351 | σ 5.00 t +0.341 | σ 4.00 t +0.267 |
| lg 2x | σ 4.00 t +0.433 | σ 4.00 t +0.412 | σ 5.00 t +0.432 | σ 5.00 t +0.413 | σ 5.00 t +0.379 | σ 5.00 t +0.359 | σ 5.00 t +0.338 | σ 6.00 t +0.371 |
| md 1x | σ 2.00 t +0.398 | σ 2.50 t +0.416 | σ 2.50 t +0.383 | σ 1.75 t +0.317 | | | | |
| md 2x | σ 3.50 t +0.511 | σ 3.50 t +0.509 | σ 4.00 t +0.521 | σ 4.00 t +0.507 | | | | |
| ml 1x | σ 2.50 t +0.365 | σ 2.50 t +0.353 | σ 3.00 t +0.353 | σ 3.50 t +0.374 | σ 4.00 t +0.367 | σ 2.50 t +0.276 | | |
| ml 2x | σ 4.00 t +0.488 | σ 4.00 t +0.480 | σ 4.00 t +0.460 | σ 4.00 t +0.438 | σ 5.00 t +0.454 | σ 5.00 t +0.441 | | |

With the heavy width held fixed per cell (the two-component columns of `depth`), the sharp component's
amplitude falls with depth at **both** scales, and faster at 2x:

| | u 20–28 | u 28–36 | u 36–44 | u 44–48 |
| --- | --- | --- | --- | --- |
| md 1x, pitch 32: σ_sharp / t_sharp / k | 1.25 / 0.283 / 0.48 | 1.25 / 0.256 / 0.53 | 1.25 / 0.234 / 0.57 | 1.25 / 0.225 / 0.58 |
| md 2x, pitch 32: σ_sharp / t_sharp / k | 0.50 / 0.094 / 0.82 | 0.50 / 0.067 / 0.87 | 0.50 / 0.018 / 0.97 | 1.75 / 0.000 / 1.00 |

**Reading — §5.49 §7's depth claim, refined.** Its 1x half ("the sharp σ-1.25 component keeps its
width and loses amplitude linearly with depth over the whole half-span, `rrect-lg` 0.166 → 0.041 over
u 24 → 76") reproduces exactly: 0.169 at u 20–28 falling to 0.040 at u 76–80 with σ pinned at
1.25 → 0.75. Its 2x half ("its σ widens instead, 2 → 3 → 4 → 5 CSS px from the band to the centre")
is **the same mechanism seen through a single-component fit**, not a widening kernel: with the two
components separated, the 2x sharp component keeps a σ of 0.5 CSS px (1 device px) and its amplitude
collapses to zero by mid-depth (0.094 → 0.000 over u 20 → 48 on `rrect-md`), which leaves the heavy
component alone and makes a one-Gaussian fit report a wider σ the deeper it looks. The reference
runs one opacity ramp on the sharp term at both scales — §5.50 §2's "0.5 at the edge falling to 0 at
the centre" — and at 2x the ramp starts lower and reaches zero sooner.

---

## 3. The impulse kernel

The deep interior (u ≥ 20, outside the lens) of one cell over all five pitches at once, fitted as a
pair of operators with non-negative amplitudes: pitches 4 and 8 constrain the core, 32 and 64 the
base. The `quarter` core is parameter-free — the plate downsampled to the quarter-device-scale buffer
(a 4-device-px box: 4 CSS px at 1x, 2 CSS px at 2x) and bilinearly upsampled, which is what §5.50 §2
says the sharp term is.

| cell | Gaussian core | box core | quarter-buffer core | base σ (CSS / device) | base share |
| --- | --- | --- | --- | --- | --- |
| md 1x | σ 1.25, rms 0.0125 | **w 4.00, rms 0.0116** | rms 0.0116 | 9 / 9 | 0.501 |
| ml 1x | σ 1.25, rms 0.0140 | **w 4.00, rms 0.0135** | rms 0.0135 | 9 / 9 | 0.597 |
| lg 1x | σ 1.25, rms 0.0172 | **w 4.00, rms 0.0170** | rms 0.0170 | 9 / 9 | 0.688 |
| md 2x | σ 0.50, rms 0.0206 | w 1.50, rms 0.0205 | rms 0.0205 | 4 / 8 | 0.901 |
| ml 2x | σ 0.50, rms 0.0194 | w 1.50, rms 0.0193 | rms 0.0194 | 5 / 10 | 0.962 |
| lg 2x | σ 0.50, rms 0.0190 | w 1.00, rms 0.0190 | rms 0.0190 | 5 / 10 | 1.000 |

**Reading.** At 1x the core is **flat-topped and exactly 4 CSS px wide** — the box core's optimum
lands on 4.00 on all three spans and ties the parameter-free quarter-buffer operator to four
decimals, while the best Gaussian is measurably worse (0.0116 against 0.0125 on `rrect-md`). That is
the quarter-device-scale buffer's own pixel footprint, read off the captures without assuming it.
At 2x the same operator wins by a hair at a width of 1.0–1.5 CSS px against the buffer's 2 CSS px,
and the discrimination between box and Gaussian disappears — because at 2x the core carries so
little amplitude (share of the base 0.90–1.00) that its shape is barely observable. The base is
**σ 9 device px at 1x and 8–10 device px at 2x**: one number in device pixels, not in points. This
is the single most important number in this document.

Two caveats. This fit holds the core/base mix constant over the band, so it absorbs the depth ramp of
§2 into an average and its RMS (0.012–0.021) is above the joint fits of §6. And §5.49 §7's 1x base
"σ ≈ 14 with 0.18 share" was read from the dedicated impulse backdrop with a Gaussian fitted to a
flat-topped core; on the checkerboard pitch axis, with the core's shape fitted rather than assumed,
the base is σ 9 and carries half the transmission. The two are different decompositions of the same
kernel and the pitch-axis one is the identifiable one.

---

## 4. Level and transmission

All 56 scenes present in both probes, interior mean of the same box, plate statistics under the same
mask. §5.49 §7 claims the reference's interior mean is scale-invariant to ±0.001 on every cell; on
the probe bed **31 of 56 cells** are within ±0.001 and the largest |Δ| is 0.095. The plate under the
box is identical between the scales on every row below (plate mean Δ = 0.0000), so the difference is
the material's, not the backdrop's.

| cell | mean 1x | mean 2x | Δ | retained 1x | retained 2x | t 1x | t 2x |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `checkerboard-lc16__rrect-sm` | 0.8010 | 0.8964 | +0.0954 | 0.219 | 0.122 | +0.263 | +0.146 |
| `hc-text-28__rrect-sm` | 0.6814 | 0.5956 | −0.0859 | 0.293 | 0.358 | +0.342 | +0.403 |
| `hc-text-7__rrect-sm` | 0.6748 | 0.7499 | +0.0751 | 0.146 | 0.172 | +0.763 | +0.432 |
| `checkerboard-32__capsule-button__rest-tint-orange` | 0.3519 | 0.3988 | +0.0469 | 0.072 | 0.037 | +0.085 | +0.046 |
| `checkerboard-64__capsule-button` | 0.6649 | 0.7060 | +0.0412 | 0.385 | 0.438 | +0.408 | +0.472 |
| `hc-text__rrect-sm` | 0.7244 | 0.7491 | +0.0247 | 0.266 | 0.253 | +0.685 | +0.285 |
| `checkerboard-64__rrect-sm` | 0.9681 | 0.9731 | +0.0050 | (plate uniform under the box) | | | |
| `checkerboard-8__rrect-sm` | 0.6112 | 0.6081 | −0.0031 | 0.242 | 0.172 | +0.413 | +0.215 |

(Every other cell is within ±0.003; the full list is in `g3-measurement.json` under
`level.mean_scale_invariance`.)

**Reading.** The mean is scale-invariant where §5.49 §7 measured it — every `rrect-md`, `-ml` and
`-lg` checkerboard cell is within 0.0021 and the three `photo` cells within 0.0011 — but
it is **not** scale-invariant on the small spans over high-contrast structured backdrops. Two of the
six offenders (`lc16__rrect-sm`, `checkerboard-64__rrect-sm`) are the frequency-settled cells of
§5.53 and their Δ equals their own two-state distance to three decimals, so they say nothing about
scale. The other four — the three `hc-text` `rrect-sm` rows and two `capsule-button` rows — are
unanimous at both scales in both provenances, so their 0.02–0.09 is a real scale-dependent level. It
sits exactly where §5.50 §2's thin-material inputs live (`tracksLuma` 1 below the span-64 knee, the
face black and fill alpha that adapt to the backdrop), and the natural mechanism is that what the
material adapts its level to is what the quarter-scale buffer resolves — which is a different image
at the two scales. Not measured further here; named as a gap.

Transmission by span, pitch 16 → the pitch axis (1x → 2x): sm 0.340 → 0.367, cap 0.331 → 0.376,
md 0.246 → 0.413, ml 0.165 → (flattened), lg 0.093 → (flattened); at pitch 32, sm 0.408 → 0.445,
cap 0.398 → 0.434, md 0.404 → 0.505, ml 0.355 → 0.448, lg 0.328 → 0.388. At every pitch that both
scales resolve, the 2x reference transmits 10–25% more of the backdrop's structure than the 1x one,
which is §5.49 §7's "retains 19–35% more contrast" seen on the probe's own axis.

---

## 5. The lens crossings at 2x — a check of G2, not a fit

Model-free boundary crossings with the G1 instrument (`w12lib.EdgeLines`, imported unmodified from
`../g1/`); the plate self-test is 0.0 on every cell. Only the window that assigns a crossing to a
boundary uses a prior; D = s − u is the measurement. The landed G2 law is
S = 0.745·min(0.8·span, 60), L′ = 1.337·min(0.25·span, 20), D(u) = S·(1 − u/L′)^3.69.

| cell | pitch | edge | u | D measured | D from the G2 law | Δ |
| --- | --- | --- | --- | --- | --- | --- |
| md 1x | 16 | top | 1.92 | 34.08 | 33.95 | +0.13 |
| md 1x | 16 | left/right | 2.91 / 2.93 | 29.09 / 29.07 | 29.24 / 29.12 | −0.14 / −0.06 |
| md 1x | 16 | bottom | 3.95 | 24.05 | 24.79 | −0.74 |
| md 1x | 16 | top | 7.90 | 12.10 | 12.27 | −0.17 |
| md 1x | 32 | top | 7.59 | 12.41 | 13.05 | −0.63 |
| md 1x | 64 | top | 7.58 | 12.42 | 13.07 | −0.65 |
| **md 2x** | 16 | top | 2.03 | 33.97 | 33.41 | **+0.56** |
| **md 2x** | 16 | left/right | 2.84 / 2.82 | 29.16 / 29.18 | 29.52 / 29.61 | −0.37 / −0.43 |
| **md 2x** | 16 | bottom | 3.90 | 24.10 | 24.99 | −0.89 |
| **md 2x** | 16 | top | 7.64 | 12.36 | 12.90 | −0.55 |
| **md 2x** | 32 | top | 7.44 | 12.56 | 13.41 | **−0.85** |
| **md 2x** | 64 | top | 7.62 | 12.38 | 12.97 | −0.59 |
| lg 1x | 16 | top / edges / top | 2.02 / 3.92–4.02 / 7.95 | 33.98 / 24.0 / 12.05 | 33.44 / 24.5–24.9 / 12.15 | +0.54 / −0.5…−0.8 / −0.11 |
| lg 1x | 32 | top | 7.48 | 12.52 | 13.31 | −0.79 |
| **lg 2x** | 16 | top / edges / top | 2.13 / 3.9–4.2 / 7.25 | 33.87 / 23.8–23.9 / 12.75 | 32.93 / 23.8–24.3 / 13.93 | +0.95 / ±0.3 / **−1.17** |
| **lg 2x** | 32 | top | 7.18 | 12.82 | 14.09 | **−1.27** |

At pitch 32 and 64 only two crossings per edge family are reachable (with D ≈ 40 at the contour, a
source depth below ≈ 16 CSS px is never sampled), so pitch 16 from the same probe is included; it
also reproduces §5.49 §2's published rows.

**Reading — G2 stands at 2x.** The measured field at 2x is the same curve as at 1x: 34 at u ≈ 2,
29 at 3, 24 at 4, 12.4 at 7.5, ≈ 0 at 20, on both spans and every pitch. Against the landed law the
2x gap is **within 0.9 px on `rrect-md` and 1.3 px on `rrect-lg`**, against 0.8 px worst at 1x. The
sign is consistent: the law is a little short at the contour (+0.6 to +1.0 px of reference beyond it)
and a little long at mid-depth (−0.6 to −1.3 px), slightly more so at 2x and on the largest span, and
its zero crossing sits ≈ 0.5–1.0 px inside the reference's at 2x. This is a check, so nothing is
fitted; the residual shape is the same one §5.49 §2 recorded at 1x and is not a scale effect.

---

## 6. The candidate forms

Fit set: spans 32 / 44 / 96 / 128 at **both** scales × four pitches (8 / 16 / 32 / 64), the same
inset box, (a, t) free per (span, scale) as the level laws' nuisance. Holdout: `rrect-lg` at both
scales, never fitted. Each grid sweep is computed from least-squares moments and the winner is
re-evaluated on the images; the two agree to < 2 × 10⁻⁴ (`moment_check`, asserted).

| form | fit RMS | holdout RMS | 1x fit | 1x holdout | 2x fit | 2x holdout |
| --- | --- | --- | --- | --- | --- | --- |
| **F1 GPU, σ_sharp CSS, k + scale term** | **0.0179** | **0.0197** | 0.0181 | 0.0188 | 0.0179 | 0.0200 |
| F2 quarter buffer + ramp scale term | 0.0201 | 0.0209 | 0.0182 | 0.0269 | 0.0206 | 0.0191 |
| F1 GPU, σ_sharp CSS, k shared | 0.0266 | 0.0232 | 0.0342 | 0.0386 | 0.0243 | 0.0174 |
| F1 CSS, σ_sharp CSS, k + scale term | 0.0268 | 0.0272 | 0.0395 | 0.0355 | 0.0225 | 0.0247 |
| F1 GPU, σ_sharp device, k shared | 0.0282 | 0.0255 | 0.0445 | 0.0408 | 0.0223 | 0.0200 |
| F2 quarter buffer (box or bilinear, no scale term) | 0.0301 | 0.0245 | 0.0457 | 0.0284 | 0.0246 | 0.0234 |
| F1 CSS, σ_sharp CSS, k shared | 0.0317 | 0.0245 | 0.0586 | 0.0440 | 0.0199 | 0.0164 |
| F1 CSS, σ_sharp device, k shared | 0.0336 | 0.0250 | 0.0619 | 0.0452 | 0.0214 | 0.0164 |
| F2 CSS, one blur σ = c·4r/scale | 0.0343 | 0.0275 | 0.0652 | 0.0511 | 0.0202 | 0.0171 |
| F0 CSS, σ ÷ scale | 0.0371 | 0.0281 | 0.0564 | 0.0376 | 0.0303 | 0.0252 |
| **F0 GPU, the landed law in CSS px** | 0.0421 | 0.0307 | **0.0164** | **0.0174** | **0.0464** | **0.0332** |
| F0 CSS, the landed law in CSS px | 0.0430 | 0.0306 | 0.0564 | 0.0376 | 0.0389 | 0.0286 |
| F0 GPU, σ ÷ scale | 0.0431 | 0.0319 | 0.0164 | 0.0174 | 0.0475 | 0.0346 |

Winning constants:

- **F1 GPU with the scale term** — σ_heavy **9.0 device px** (4.5 CSS px at 2x, 9.0 at 1x),
  σ_sharp **1.0 CSS px**, k = k₀ + (1 − k₀)·smoothstep(32, spanMax, span) with k₀ **0.3**,
  spanMax **224**, and **Δk = +0.4 at 2x** (the share of the heavy component is 0.4 higher at the
  second scale, clamped at 1).
- F1 GPU without the scale term — σ_heavy 11 device px, σ_sharp 2.0 CSS, k₀ 0.4, spanMax 192.
- F2 — σ_buffer = **0.8·r** buffer px, i.e. 4·0.8·r/scale CSS px (7.9 at 1x and 4.0 at 2x on
  `rrect-md`; 12.8 / 6.4 on `rrect-lg`), ramp weight 0.5 at the contour rising to 1 at u = span with
  γ 2, plus **Δw = +0.5 at 2x**. Without the scale term: c 0.8, w₀ 0.3, end 0.75, γ 0.25.
- The box and bilinear downsample filters are indistinguishable (identical to four decimals).

**Each constant at its own minimum** (one-dimensional sweeps with the others held, RMS on the fit set):

| F1 GPU + scale term | | | | | | | | | |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| σ_heavy (device px) | 6: .0333 | 7: .0255 | 8: .0201 | **9: .0179** | 10: .0190 | 11: .0223 | 12: .0265 | 14: .0353 | 16: .0428 |
| σ_sharp (CSS px) | 0.75: .0187 | **1.0: .0179** | 1.25: .0181 | 1.5: .0188 | 1.75: .0199 | 2.0: .0211 | | | |
| k₀ | 0.2: .0190 | **0.3: .0179** | 0.4: .0190 | 0.5: .0219 | 0.6: .0253 | 0.7: .0274 | | | |
| spanMax | 128: .0289 | 160: .0227 | 192: .0186 | **224: .0179** | 256: .0193 | 320: .0242 | | | |
| Δk at 2x | 0.0: .0405 | 0.2: .0267 | 0.3: .0204 | 0.35: .0182 | **0.4: .0179** | 0.45: .0183 | 0.5: .0194 | 0.6: .0213 | |

| F2 + ramp scale term | | | | | | | |
| --- | --- | --- | --- | --- | --- | --- | --- |
| c | 0.6: .0249 | 0.7: .0202 | **0.8: .0201** | 0.9: .0236 | 1.0: .0287 | 1.25: .0420 | 1.6: .0568 |
| w₀ | 0.2: .0349 | 0.3: .0278 | 0.4: .0220 | **0.5: .0201** | 0.6: .0206 | 0.7: .0223 | |
| end (fraction of span) | 0.25: .0348 | 0.375: .0284 | 0.5: .0233 | 0.75: .0203 | **1.0: .0201** | | |
| γ | 0.25: .0280 | 0.5: .0239 | 0.75: .0218 | 1.0: .0209 | 1.5: .0202 | **2.0: .0201** | |
| Δw at 2x | 0.0: .0465 | 0.2: .0335 | 0.3: .0270 | 0.4: .0217 | **0.5: .0201** | 0.6: .0201 | |

Every F1 constant sits at an interior minimum of its own sweep, Δk included (0.35 → 0.0182,
0.4 → 0.0179, 0.45 → 0.0183). Two of F2's do not: `end` and γ ride the top of their grids and Δw is
flat from 0.5 to 0.6 — the parametrised ramp is being pushed toward "sharp term suppressed until
deep, then nothing", which is a sign the mechanism is being bent rather than fitted.

**Per-pitch residual structure at 2x** (model contrast ÷ reference contrast; 1.00 is exact):

| | p8 | p16 | p32 | p64 |
| --- | --- | --- | --- | --- |
| F0 landed — cap / md / ml / lg | 1.29 / 3.99 / 3.68 / 2.92 | 0.89 / 0.93 / 0.92 / 0.91 | 0.90 / 0.85 / 0.83 / 0.86 | 1.03 / 0.97 / 0.96 / 0.98 |
| F1 + scale term — cap / md / ml / lg | 0.77 / 1.41 / 0.51 / 0.52 | 0.89 / 0.93 / 1.00 / 1.26 | 0.96 / 0.99 / 1.00 / 1.03 | 1.07 / 1.01 / 0.99 / 0.93 |
| F2 + scale term — cap / md / ml / lg | 1.07 / 0.82 / 0.19 / 0.02 | 1.04 / 0.96 / 0.82 / 0.68 | 0.97 / 1.00 / 1.01 / 1.02 | 0.96 / 1.01 / 1.03 / 1.02 |

The landed law's 2x failure is concentrated at pitch 8, where it retains **three to four times** the
contrast the reference does on spans ≥ 96 — its σ 1.25 CSS px sharp component is 2.5 device px at 2x
and passes a fine checker the reference has erased — and a uniform 15% under-retention at pitch 32.
F1 with the scale term removes both (0.99–1.03 at pitch 32 and 64 on every span); what it has left is
a mild over-retention at pitch 8 on `rrect-md` (1.41) and a 26% over-retention at pitch 16 on the
holdout. F2 goes the other way at the fine pitches on the large spans (0.02–0.19 at pitch 8), which
is the same over-suppression its grid-edge ramp bought.

**What each tier can carry.** The GPU tier's body is mip-based, and the quarter-device-scale buffer
is exactly mip level 2 of a full-resolution backdrop texture, so F2's mechanism is renderable in kind
— a level-2 fetch as the sharp term and a blurred level-2 fetch as the heavy one — with the ramp
already expressible as the existing per-pixel scatter weight. F1 needs nothing new at all: it is the
landed two-component mix with σ_heavy read in device px (`σ_css = 9 / devicePixelRatio`) and one
extra term on the scatter weight. The CSS tier has one `blur()` whose σ in CSS px may be any function
of span and `devicePixelRatio`, and it cannot carry a sharp leak beside a heavy blur at all; its
ceiling — the best free single σ per (span, scale), pooled over the four pitches — is

| | sm 32 | cap 44 | md 96 | ml 128 | lg 160 |
| --- | --- | --- | --- | --- | --- |
| 1x: σ CSS (device) / RMS | 2.50 (2.5) / .0520 | 1.50 (1.5) / .0192 | 2.00 (2.0) / .0333 | 2.50 (2.5) / .0361 | 6.00 (6.0) / .0342 |
| 2x: σ CSS (device) / RMS | 3.00 (6.0) / .0456 | 2.50 (5.0) / .0274 | 4.00 (8.0) / .0163 | 5.00 (10.0) / .0168 | 5.00 (10.0) / .0169 |

— so the CSS tier's own best σ is **larger in CSS px at 2x**, by 1.5–2×, and its residual at 2x
(0.016–0.046) is half its residual at 1x (0.019–0.052). One blur can nearly be the 2x reference and
cannot be the 1x one. Any CSS law that lands must therefore carry a `devicePixelRatio` term of its
own, in the opposite direction to the GPU tier's device-pixel σ, and the 1x CSS rows stay where they
are.

---

## 7. The photo family, as the null check

The candidates laid over the `photo` plate with only (a, t) free per cell, against the landed model
(§5.41 §3's method), at both scales:

| | sm 1x | md 1x | lg 1x | overall 1x | sm 2x | md 2x | lg 2x | overall 2x |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F0 GPU (landed) | 0.0040 | 0.0099 | 0.0154 | **0.0140** | 0.0047 | 0.0113 | 0.0160 | **0.0147** |
| F1 GPU + scale term | 0.0039 | 0.0100 | 0.0155 | 0.0141 | 0.0051 | 0.0111 | 0.0171 | 0.0156 |
| F2 GPU + scale term | 0.0045 | 0.0098 | 0.0158 | 0.0143 | 0.0045 | 0.0111 | 0.0161 | 0.0148 |
| F0 CSS | 0.0053 | 0.0099 | 0.0155 | 0.0141 | 0.0062 | 0.0118 | 0.0161 | 0.0150 |
| F1 CSS (k shared) | 0.0047 | 0.0101 | 0.0156 | 0.0142 | 0.0047 | 0.0112 | 0.0166 | 0.0152 |

**Reading.** The null is neutral at 1x (every form within 0.0003 of the landed one) and mildly
**negative for F1 at 2x**: 0.0156 against the landed 0.0147, all of it on `rrect-lg` (0.0171 against
0.0160). §5.41 §3's photo family *improved* under the 1x law; this one does not improve under F1 at
2x. It is a small number on a broadband backdrop where blur width is nearly unobservable, and F2 —
the mechanism with a device-invariant kernel and no CSS-px σ — is neutral there (0.0148), which
points at F1's σ_sharp of 1.0 CSS px (2 device px at 2x) as the term the photo plate dislikes. Named
as a gap, not resolved.

---

## What the declaration should carry

(Superseded by section 8.4, which holds every landed 1x constant and reaches the same 2x result;
this list is what the evidence of sections 1–7 alone supported.)

1. **The form.** F1 in the GPU tier: the landed two-component body with **σ_heavy fixed in device
   pixels** and **one scale term on the scatter weight**. It is the only candidate that fits both
   probes at once, it needs no new pass structure, and every one of its constants sits at an interior
   minimum of its own sweep.
2. **The constants**, on the declared grid with `rrect-lg` held out at both scales:
   σ_heavy **9.0 device px** (`blurSigma × sizeScatterGainMax` read as a device-pixel quantity),
   σ_sharp **1.0 CSS px**, `sizeScatterFloor` **0.3**, `sizeScatterSpanMax` **224**, and a new
   scale term **Δk = +0.4 at devicePixelRatio 2** (equivalently: the scatter weight's floor and its
   whole curve shift up by 0.4·(dpr − 1), clamped to 1).
3. **The holdout numbers.** Fit 0.0179, holdout 0.0197; per scale, 1x fit 0.0181 / holdout 0.0188 and
   2x fit 0.0179 / holdout 0.0200. The landed law on the same sets: fit 0.0421, holdout 0.0307
   (1x 0.0164 / 0.0174, 2x 0.0464 / 0.0332). The 1x fit worsens from 0.0164 to 0.0181 — **the price
   of one law for two beds is 0.0017 of 1x residual** — and that is a number the user should see
   before it lands, because W12's own stop is "no 1x row below its G2-landing value by more than
   0.002".
4. **The CSS tier is a separate law and a worse one.** Its best possible single blur cannot be the 1x
   reference (per-cell RMS 0.019–0.052 at the free optimum) and nearly can be the 2x one
   (0.016–0.046). Whatever CSS law is declared must carry its own `devicePixelRatio` term, in CSS px
   *upward* with the scale (best free σ: md 2.0 → 4.0, ml 2.5 → 5.0, lg 6.0 → 5.0 CSS px), and the
   1x CSS rows will not move.
5. **The residual gaps that can be named now.**
   - The photo family at 2x costs 0.0009 overall and 0.0011 on `rrect-lg` under F1 (§7).
   - F1 still over-retains pitch-8 contrast on `rrect-md` at 2x (1.41×) and pitch-16 contrast on the
     holdout (1.26×).
   - The interior mean is not scale-invariant on the small spans over text and high-contrast
     backdrops (up to 0.086 on unanimous cells, §4) — a level question, not a body question, and this
     round does not touch it.
   - The landed G2 lens is 0.6–1.3 px short of the reference's field at mid-depth at 2x, a little
     more than at 1x and most on `rrect-lg` (§5).
   - F2, the reference's *actual* mechanism, is not the recommendation: as parametrised here it needs
     the same size of scale term F1 does and two of its four constants ride the grid edge. That it
     needs one at all is the finding — the quarter-buffer kernel alone does not explain why the 1x
     material leaks so much more of the unblurred buffer than the 2x one — and it should be recorded
     as the open mechanism question rather than as a rejected form.

## Limits of this measurement

- **The virtual display.** The 2x bed is the virtual HiDPI display of §5.53, not a Retina panel.
  §5.50 §2 exonerates it for the blur (the material's own `CABackdropLayer.scale` of 0.25 makes the
  blur a device-pixel quantity, which is exactly what §3 measures), but nothing here re-tests that.
- **The frequency-settled cells.** Three 2x `rrect-sm` cells hold two settled states; on those rows a
  residual below 0.10–0.24 of linear luminance is the material's own spread (§1). They are in the fit
  set — excluding them is a variant the declaration may want and this document does not run.
- **Identifiability.** A blurred plate that has lost 95% of its contrast under the box carries no
  information about its own width; those cells are flagged rather than fitted, and the σ and t in
  flagged rows of Tables 1a/1b are not measurements. Pitch 4 is at that ceiling on every cell.
- **The lens is excluded, not modelled.** Every band and box reading starts at u = 20 or at the
  5.41 inset, outside the lens; the near-contour body is G1's and G2's, not this round's.
- **One kernel per cell, not per depth.** §3's kernel fit holds the mix constant over the band and so
  averages the depth ramp §2 measures; its RMS is correspondingly above §6's.
- **The crossings' assignment prior.** D = s − u is model-free, but which boundary a crossing belongs
  to is decided with §5.49 §2's published profile as the window. At pitch 32 and 64 only two
  crossings per edge family are reachable at all.
- **The CSS ceiling is a ceiling, not a law.** It is the best free σ per cell; no CSS form that lands
  can reach it at every span at once.

## How to reproduce

From the repository root, with the analysis venv
(`/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python`):

```
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_interior.py   # tables 1a, 1b, the checks
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_depth.py     # table 2
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_kernel.py    # table 3
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_level.py     # table 4
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_lens2x.py    # table 5
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_forms.py     # table 6 (~80 s)
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_photo.py     # table 7
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_variants.py  # section 8.1–8.2 (~4 min)
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_dryrun.py    # section 8.3
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_dryrun2.py   # section 9 (~3 min)
python packages/calibration/results/2026-09-03-w12-lens/g3/g3_report.py    # merges parts/ → g3-measurement.json, prints every table
```

Each script writes `parts/<name>.json`; `g3_report.py` merges them into `g3-measurement.json` and
prints the tables above verbatim. Two inputs live outside the repository and are named where they are
used: the five 2x probe run snapshots (for §1's noise bar) and the 1x probe's backdrop rasters (used
only to prove the analytic plate generator, which every reading actually uses).

---

## 8. The 1x-preserving variant, the exclusion refit, and the canonical SSIM dry run

Section 6's winner (F1) moves four constants that are already landed at 1x — σ_sharp 1.25 → 1.0,
`sizeScatterFloor` 0.4 → 0.3, `sizeScatterSpanMax` 256 → 224, the heavy width 10 → 9 — and pays
0.0017 of 1x residual for it. W12's stop is on the 1x rows, so this section asks what is left if
every landed 1x constant is held and **only scale terms** are added, refits under the exclusion of
the frequency-settled cells, and runs §5.41 §4's SSIM dry run on the canonical pitch-16 cells.

### 8.1 F1′ — the landed law at dpr 1, scale terms at dpr 2

F1′ is `σ_sharp = blurSigma 1.25`, `σ_heavy = blurSigma × sizeScatterGainMax = 10` CSS px,
`k = 0.4 + 0.6·smoothstep(32, 256, span)` — all landed and untouched — plus two scale terms:
σ_heavy read in device px (5.0 CSS px at 2x) and `k′ = min(k + Δk·(dpr − 1), 1)`. Δk is fitted on the
2x probe alone; the 1x numbers are the landed law's **by construction** and are asserted equal to it
in the script (fit 0.0164, holdout 0.0174). Three treatments of the sharp term at 2x:

| variant | σ_sharp at 2x | σ_heavy at 2x | Δk | 2x fit | 2x holdout | 1x fit / holdout | photo 2x |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1′ (a) | 1.25 CSS px | 5.0 (10 device) | 0.35 | 0.0203 | 0.0169 | 0.0164 / 0.0174 | 0.0153 |
| **F1′ (b)** | **0.625 (1.25 device)** | **5.0 (10 device)** | **0.35** | **0.0192** | **0.0169** | **0.0164 / 0.0174** | **0.0153** |
| F1′ (c) | 1.25 CSS px | 4.5 (9 device) | 0.35 | 0.0193 | 0.0200 | 0.0164 / 0.0174 | 0.0156 |
| F1 (section 6) | 1.0 CSS px | 4.5 (9 device) | 0.40 | 0.0179 | 0.0200 | 0.0181 / 0.0188 | 0.0156 |
| F0, the landed law | 1.25 CSS px | 10.0 CSS px | — | 0.0464 | 0.0332 | 0.0164 / 0.0174 | 0.0147 |

Δk sweeps (2x fit set), each with a clear interior minimum at 0.35:

| Δk | 0.20 | 0.25 | 0.30 | **0.35** | 0.40 | 0.45 | 0.50 | 0.60 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F1′ (a) | .0252 | .0225 | .0208 | **.0203** | .0215 | .0235 | .0254 | .0281 |
| F1′ (b) | .0287 | .0243 | .0209 | **.0192** | .0201 | .0223 | .0247 | .0281 |
| F1′ (c) | .0267 | .0236 | .0210 | **.0193** | .0196 | .0208 | .0223 | .0247 |

**Reading.** Reading the sharp term in device pixels too — variant (b), 1.25 device px = 0.625 CSS px
at 2x — is worth 0.0011 of 2x residual over leaving it at 1.25 CSS px, and it agrees with §3's
measurement that the 2x core is 0.5–1.5 CSS px wide. Reading the heavy width as 9 device px instead
of 10 buys 0.0010 on the fit set (c against a) and costs 0.0031 on the holdout, so on this evidence
10 device pixels — which is what the landed constant already is — is the better of the two.

**How far F1′ (b) sits from F1 at 2x: 0.0013 on the fit set (0.0192 against 0.0179) and −0.0031 on
the holdout (0.0169 against 0.0200) — it is better on the untouched holdout at both scales.** That
0.0013 is inside the fit's own sensitivity: F1's one-dimensional sweeps move by 0.0011 for one step
of σ_heavy (9 → 10 device px), 0.0011 for one step of k₀, 0.0007–0.0014 for one step of spanMax and
0.0003 for one step of Δk. The 1x price, by contrast, is not inside anything: F1 costs 0.0017 there
and F1′ costs exactly zero.

Per-pitch contrast ratio at 2x (model std ÷ reference std; 1.00 is exact):

| | p8 | p16 | p32 | p64 |
| --- | --- | --- | --- | --- |
| F1′ (b) — cap / md / ml / lg | 0.73 / 1.53 / 0.42 / 0.26 | 0.82 / 0.86 / 0.89 / 1.11 | 0.94 / 0.98 / 1.00 / 1.03 | 1.10 / 1.03 / 1.01 / 0.96 |
| F1′ (c) — cap / md / ml / lg | 0.62 / 1.40 / 0.63 / 0.52 | 0.86 / 0.94 / 1.01 / 1.26 | 0.95 / 0.99 / 1.00 / 1.03 | 1.09 / 1.01 / 0.99 / 0.93 |
| F1 (section 6) — cap / md / ml / lg | 0.77 / 1.41 / 0.51 / 0.52 | 0.89 / 0.93 / 1.00 / 1.26 | 0.96 / 0.99 / 1.00 / 1.03 | 1.07 / 1.01 / 0.99 / 0.93 |
| F0, the landed law | 1.29 / 3.99 / 3.68 / 2.92 | 0.89 / 0.93 / 0.92 / 0.91 | 0.90 / 0.85 / 0.83 / 0.86 | 1.03 / 0.97 / 0.96 / 0.98 |

At pitch 32 and 64 — the pitches the 2x reference actually resolves — F1′ (b) is within 0.06 of exact
on the three large spans and within 0.10 on the capsule, the same as F1. Its residual structure differs from F1's only at the pitches where the
2x reference has nothing left to match: it under-retains at pitch 8 on the large spans (0.26–0.42)
where F1 under-retains slightly less, and it is nearer at pitch 16 on the holdout (1.11 against
F1's 1.26). The landed law's three-to-four-fold over-retention at pitch 8 is removed by both.

The photo null at 2x prefers F1′ (b) as well: 0.0153 against F1's 0.0156, with the landed law at
0.0147; the gap to the landed law halves but does not close.

### 8.2 The exclusion refit — are any constants the settled cells'?

Claims §5.53 §2 leaves three 2x `rrect-sm` cells frequency-settled. Two of them are on fit pitches
(`checkerboard-8`, `checkerboard-64`); the third (`checkerboard-lc16`) is not a fit pitch and never
entered the fit. Refitting with those cells dropped:

| | σ_heavy (device px) | σ_sharp | k₀ | spanMax | Δk | fit | holdout |
| --- | --- | --- | --- | --- | --- | --- | --- |
| F1, all cells | 9.0 | 1.0 | 0.3 | 224 | 0.40 | 0.0179 | 0.0197 |
| F1, settled cells excluded | 9.0 | 1.0 | **0.2** | **192** | 0.40 | 0.0174 | **0.0220** |
| F1′ (a) / (b) / (c), all cells | (10 / 10 / 9) | — | 0.4 | 256 | **0.35** | .0203 / .0192 / .0193 | — |
| F1′ (a) / (b) / (c), excluded | (10 / 10 / 9) | — | 0.4 | 256 | **0.35** | .0200 / .0190 / .0188 | — |

**Reading.** Two of F1's five constants move when the settled cells come out — the scatter floor
0.3 → 0.2 and spanMax 224 → 192 — and the holdout gets *worse* (0.0197 → 0.0220), which says those
two were partly fitted to cells whose own two states are 0.10–0.24 apart. σ_heavy 9 device px and
Δk 0.4 do not move. F1′ has only one free parameter and it does not move at all: Δk stays 0.35 in
every variant under both fit sets, with its 2x RMS shifting by at most 0.0005. On the robustness
axis F1′ is the stronger claim.

### 8.3 The canonical SSIM dry run

§5.41 §4's method: vitrea's own capture with its deep body — the §5.41 interior box, rim band and
outside untouched — replaced by the candidate law at the **reference** cell's own level and
transmission, hue kept by scaling RGB by the luminance ratio; then whole-crop `ssimMean` against the
native fixture. Baselines are the material now on `main`: the webgpu tier from the ω-0.8 round
(`web-captures-g2b/`) and the CSS tier from the G2 landing (`web-captures-g2/`). The CSS law is
derived from the same constants by the K5 contract,
σ_css = σ_sharp·(1 + (gain_eff − 1)·k′) with gain_eff = σ_heavy,css / σ_sharp.

**Instrument check.** The numpy SSIM replica reproduces the `before` column against the scratch
matrices those captures were scored into on all twenty rows: largest |replica − matrix| = **0.00000**.

| row | bound | floor | before | F0 | F1 | F1′ | F1−F0 | F1′−F0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| webgpu / rrect-sm / 1x | 0.88 | — | 0.9988 | 0.9979 | 0.9979 | 0.9979 | −0.0001 | +0.0000 |
| webgpu / capsule-button / 1x | 0.88 | — | 0.9852 | 0.9840 | 0.9838 | 0.9840 | −0.0001 | +0.0000 |
| webgpu / rrect-md / 1x | 0.88 | — | 0.9695 | 0.9707 | 0.9703 | 0.9707 | −0.0004 | +0.0000 |
| webgpu / rrect-ml / 1x | 0.88 | — | 0.9482 | 0.9501 | 0.9497 | 0.9501 | −0.0005 | +0.0000 |
| webgpu / rrect-lg / 1x | 0.88 | — | 0.9428 | 0.9454 | 0.9451 | 0.9454 | −0.0003 | +0.0000 |
| **webgpu / rrect-sm / 2x** | 0.93 | — | 0.9978 | 0.9972 | 0.9972 | 0.9974 | +0.0000 | +0.0002 |
| **webgpu / capsule-button / 2x** | 0.93 | — | 0.9836 | 0.9826 | 0.9829 | 0.9832 | +0.0002 | +0.0006 |
| **webgpu / rrect-md / 2x** | 0.93 | — | 0.9517 | 0.9497 | 0.9542 | **0.9545** | +0.0045 | +0.0047 |
| **webgpu / rrect-ml / 2x** | 0.93 | 0.9013 | 0.9158 | 0.9110 | 0.9219 | **0.9219** | +0.0109 | +0.0109 |
| **webgpu / rrect-lg / 2x** | 0.93 | 0.9002 | 0.9113 | 0.9084 | 0.9164 | **0.9164** | +0.0080 | +0.0081 |
| css / rrect-sm / 1x | 0.90 | — | 0.9853 | 0.9851 | 0.9857 | 0.9851 | +0.0006 | +0.0000 |
| css / capsule-button / 1x | 0.90 | — | 0.9612 | 0.9610 | 0.9620 | 0.9610 | +0.0011 | +0.0000 |
| css / rrect-md / 1x | 0.90 | 0.8952 | 0.8963 | 0.8952 | 0.8959 | 0.8952 | +0.0007 | +0.0000 |
| css / rrect-ml / 1x | 0.90 | 0.8470 | 0.8481 | 0.8475 | 0.8475 | 0.8475 | +0.0001 | +0.0000 |
| css / rrect-lg / 1x | 0.90 | 0.8361 | 0.8372 | 0.8321 | 0.8321 | 0.8321 | −0.0000 | +0.0000 |
| css / rrect-sm / 2x | 0.92 | — | 0.9883 | 0.9878 | 0.9880 | 0.9879 | +0.0002 | +0.0001 |
| css / capsule-button / 2x | 0.92 | — | 0.9705 | 0.9697 | 0.9699 | 0.9698 | +0.0002 | +0.0001 |
| css / rrect-md / 2x | 0.92 | 0.9159 | 0.9169 | 0.9184 | 0.9188 | 0.9187 | +0.0004 | +0.0003 |
| css / rrect-ml / 2x | 0.92 | 0.8754 | 0.8765 | 0.8795 | 0.8794 | 0.8795 | −0.0001 | −0.0000 |
| css / rrect-lg / 2x | 0.92 | 0.8686 | 0.8696 | 0.8700 | 0.8699 | 0.8700 | −0.0001 | −0.0000 |

**Reading — the 2x rows.** On the GPU tier the body law is worth **+0.0028 to +0.0061 of whole-crop
SSIM against the captures on `main`** at 2x on the three large spans (md 0.9517 → 0.9545,
ml 0.9158 → 0.9219, lg 0.9113 → 0.9164 under F1′), and the landed law in the same dry run goes the
*other* way (0.9497 / 0.9110 / 0.9084) — the body is measurably the 2x deficit, and replacing it with
the landed law at the reference's own level makes those rows worse. F1 and F1′ are within 0.0003 of
each other on every 2x row; F1′ is the higher of the two on three of the five and equal on the other
two. `rrect-sm`, `capsule-button` and `rrect-md` clear the 0.93 bound (0.9974 / 0.9832 / 0.9545);
`rrect-ml` and `rrect-lg` stay under it by 0.0081 and 0.0136 with the rim and the outside still
vitrea's, but clear their pinned floors with room — 0.9219 against 0.9013 and 0.9164 against 0.9002.

**Reading — the stop.** No 1x GPU row falls by more than 0.002 under either law; F1's worst is
−0.0005 (`rrect-ml`) and three of its five 1x rows rise. **Under F1′ every 1x row is +0.0000 against
the landed law by construction** — no 1x constant moves, so a landing would leave the 1x captures
byte-identical, and the F1′ column of the 1x rows is the landed law's own column, not a prediction.

One row does move down against its *capture*: `css / rrect-lg / 1x` falls 0.8372 → 0.8321 (−0.0051),
below its 0.8361 floor. That drop is identical for the landed law F0 (−0.0000 against F1 and F1′), so
it is not something the declaration would introduce: it is the dry run's own artefact on that cell —
replacing a structured CSS body with the reference's level and a single blur that cannot carry the 1x
sharp leak at any σ (§6's CSS ceiling). Since the 1x CSS constants do not move under F1′, the row's
landing prediction is *unchanged*, and this number should be read as one more measurement of what a
single `blur()` cannot do at 1x rather than as a stop. Under F1 the 1x CSS constants *do* move and
the dry run cannot separate that; that is one more reason to prefer F1′.

A caveat on the small spans: on `rrect-sm` and `capsule-button` at 1x every law, the landed one
included, loses 0.0009–0.0012 in this dry run. That is the level refit inside the box, not the body
law — those cells are lens band nearly edge to edge and carry almost no deep body (§5.38 §3).

### 8.4 What the declaration should carry — revised

(Superseded by section 9.6: this section's dry run evaluated every candidate at the reference's own
level and transmission and left the rim band untouched. Section 9 removes both normalisations.)

**Declare F1′ (b), not F1.** It is the landed law with two scale terms and nothing else:

- `σ_heavy` read as a **device-pixel** quantity: `blurSigma × sizeScatterGainMax = 10` device px,
  so 10 CSS px at dpr 1 and 5 CSS px at dpr 2. No constant changes value.
- `σ_sharp` read as a **device-pixel** quantity: `blurSigma = 1.25` device px, so 1.25 CSS px at
  dpr 1 and 0.625 at dpr 2. No constant changes value.
- One genuinely new constant, the scatter weight's scale term: **Δk = 0.35 per unit of
  (devicePixelRatio − 1)**, added to the whole curve and clamped to 1.
- `sizeScatterFloor` 0.4, `sizeScatterSpanMax` 256 and the smoothstep stay exactly as landed.

Why this rather than section 6's F1, which fits the pooled bed 0.0013 better at 2x: **(i)** its 1x
rows are byte-identical to what is landed, so W12's 1x stop cannot be tripped and the 1x claims of
§5.41 and §5.42 stand unamended; **(ii)** it is better on the untouched holdout at 2x (0.0169 against
0.0200) and on the photo null (0.0153 against 0.0156); **(iii)** its single free parameter does not
move when the frequency-settled cells are excluded, while two of F1's five do and F1's holdout
degrades when they come out; **(iv)** the 0.0013 it concedes on the fit set is one grid step of F1's
own sweeps; **(v)** in the SSIM dry run it is the equal or better of the two on all ten GPU rows. The interpretation is also simpler and matches §3's kernel directly: **the reference's body
kernel is fixed in device pixels, and the second scale changes only how much of it leaks unblurred.**

The numbers to publish with it: 1x fit 0.0164 / holdout 0.0174 (the landed values, unchanged);
2x fit 0.0192 / holdout 0.0169 against the landed law's 0.0464 / 0.0332; photo null at 2x 0.0153
against the landed 0.0147; dry-run GPU 2x rows 0.9517 → 0.9545, 0.9158 → 0.9219, 0.9113 → 0.9164 with
every 1x row unmoved.

Unchanged from §6: the CSS tier is a separate and worse story — one blur cannot carry the 1x sharp
leak (the `css / rrect-lg / 1x` row above is that fact in SSIM), the K5-derived CSS law moves the 2x
dom rows up by only 0.0003–0.0030, and the 1x dom rows should be left where they are. And the open
mechanism question stands: F2, the reference's own quarter-buffer, needs a scale term of the same
size, so nothing here explains *why* the 1x material leaks so much more of the unblurred buffer than
the 2x one.

---

## 9. The dry run redone at vitrea's own level and transmission

The G3 landing failed stop 3: the three 2x GPU texture rows fell (`rrect-md` 0.9517 → 0.9451,
`rrect-ml` 0.9158 → 0.9041, `rrect-lg` 0.9113 → 0.9078). The referee's verdict names the two
normalisations section 8's dry run rests on — it evaluated every candidate at the **reference's**
level and transmission while the runtime renders at vitrea's own, and it left the rim band untouched
while the runtime's lens reads the body at the refracted position. This section removes both, and
finds a third thing neither had accounted for.

### 9.1 The instrument

`interiorStdDev` is the compare's reading of retained structure over the **native silhouette bounded
to the component region** (`cli/measure.ts`: "One mask for both sides, and it is the NATIVE
silhouette"). The geometric replica used here is `u > 0`. Against the matrices' own rows
(`matrix-g2b.json` for `main`, `matrix-g3.json` for the landing), on all twenty webgpu rows:

| | native (replica / matrix) | main | G3 |
| --- | --- | --- | --- |
| 2x `rrect-md` | 0.1273 / 0.1272 | 0.0975 / 0.0973 | 0.0615 / 0.0611 |
| 2x `rrect-ml` | 0.1023 / 0.1018 | 0.0753 / 0.0746 | 0.0424 / 0.0411 |
| 2x `rrect-lg` | 0.0819 / 0.0810 | 0.0539 / 0.0525 | 0.0398 / 0.0379 |

Largest disagreement over the twenty rows: 0.0019. The replica is the instrument for everything
below.

### 9.2 The nominal law models `main` at both scales, and does not model the G3 build

Retained structure is transmission × the model column's own spread, so dividing a capture's interior
standard deviation by the nominal law's column gives the transmission the runtime must be applying if
the nominal law is what it renders. On the §5.41 box:

| cell | main 1x | main 2x | G3 2x |
| --- | --- | --- | --- |
| `rrect-sm` | 0.506 | 0.491 | **0.368** |
| `capsule-button` | 0.495 | 0.490 | **0.365** |
| `rrect-md` | 0.468 | 0.467 | **0.280** |
| `rrect-ml` | 0.467 | 0.454 | **0.201** |
| `rrect-lg` | 0.449 | 0.449 | **0.186** |

**Reading, and it is the finding of this section.** For the material on `main` the nominal
two-component law at one transmission per span reproduces the rendered retained structure at **both
scales** — the 1x and 2x columns agree to 0.013 or better on every span, and the number is vitrea's
own transmission (0.45–0.51), not the reference's. So the model this document has used throughout is
a valid model of what the GPU tier renders, and section 8's error was only the normalisation.

For the G3 build it is not. The same nominal law — the one the landing implemented, both σ in device
pixels and Δk 0.35 — implies a transmission of 0.19–0.37, roughly **40–60% below** the same cell's
transmission on `main`, and vitrea's transmission is not something the body law changes. The G3
capture therefore retains far less structure than its own declared law predicts. Two readings are
consistent with that and this evidence cannot separate them: either the GPU tier's mip-based body
cannot deliver a σ halved in device pixels (a nominal σ maps to a chain level, and one level's
footprint is not the nominal Gaussian), or something else in the optics pass moved with the same
constants. Either way, **the landing's 2x fall is not fully explained by the dry run's
normalisations; part of it is that the implementation did not render the declared kernel**, and that
belongs to the landing worker before any re-declaration.

Everything below therefore predicts what the declared law *would* retain, and is conditional on the
implementation delivering it.

### 9.3 The corrected dry run

vitrea's own (a, t) are read from vitrea's own capture on `main` by regressing its interior box on the
law `main` renders (r² 0.989–0.992 on every cell); they are then **held** while only the body
structure is swapped. The band is predicted rather than skipped: a pixel at depth u takes the body at
the refracted position q − D(u)·n̂ with D the landed G2 law. Predicted retained structure, 2x, over
the box and over the compare's silhouette:

| candidate | md box / sil | ml box / sil | lg box / sil |
| --- | --- | --- | --- |
| **native** | **0.1223 / 0.1273** | **0.0866 / 0.1023** | **0.0565 / 0.0819** |
| main, measured | 0.0952 / 0.0975 | 0.0699 / 0.0753 | 0.0464 / 0.0539 |
| main, reconstructed (the control) | 0.0949 / 0.0941 | 0.0695 / 0.0701 | 0.0462 / 0.0467 |
| (a) both σ device, Δk 0.00 | 0.1373 / 0.1362 | 0.1152 / 0.1162 | 0.0983 / 0.0993 |
| **(a) both σ device, Δk 0.10** | **0.1232 / 0.1218** | **0.1017 / 0.1026** | 0.0856 / 0.0866 |
| (a) both σ device, Δk 0.20 | 0.1093 / 0.1078 | 0.0887 / 0.0894 | 0.0737 / 0.0747 |
| (a) both σ device, Δk 0.35 (the landing) | 0.0894 / 0.0876 | 0.0705 / 0.0712 | 0.0697 / 0.0706 |
| (b) heavy σ device, Δk 0.00 | 0.1291 / 0.1274 | 0.1092 / 0.1102 | 0.0950 / 0.0962 |
| (b) heavy σ device, Δk 0.10 | 0.1171 / 0.1153 | 0.0978 / 0.0986 | 0.0840 / 0.0851 |
| (b) heavy σ device, Δk 0.20 | 0.1052 / 0.1034 | 0.0865 / 0.0873 | 0.0734 / 0.0744 |

The control is the check that matters: reconstructing `main` from `main`'s own law and vitrea's own
(a, t) reproduces the measured box standard deviation to 0.3% (0.0949 against 0.0952, 0.0695 against
0.0699, 0.0462 against 0.0464) and the silhouette figure to 3.5%. At 1x every candidate is identical
to `main` to four decimals on every cell, because no term of any candidate moves at dpr 1.

**Which candidate brings the GPU tier nearest native.** On the silhouette the compare actually
measures, **Δk ≈ 0.10 with both σ in device pixels**: md 0.1218 against native 0.1273, ml 0.1026
against 0.1023, lg 0.0866 against 0.0819. Δk 0.35 — the landing's — undershoots on all three even
before the implementation gap of §9.2 (0.0876 / 0.0712 / 0.0706 against native 0.1273 / 0.1023 /
0.0819), and Δk 0 overshoots on the two larger spans. The (b) family, which leaves the sharp σ in CSS
px, needs Δk 0 on `rrect-md` and Δk 0.10–0.20 on the larger spans to reach the same place, i.e. it
does not admit one Δk.

**The instrument check the referee asked for fails, in the direction §9.2 predicts.** Evaluated this
way the landing candidate ((a) Δk 0.35) predicts a silhouette standard deviation of 0.0876 / 0.0712 /
0.0706 where the G3 capture measures **0.0615 / 0.0424 / 0.0398** — the prediction retains 42% / 68% /
77% more structure than the build did. It is the same discrepancy as §9.2's transmission column, seen
per candidate rather than per span.

**SSIM is reported in the JSON but not read here.** Reconstructing `main` from `main`'s own law gives
a whole-crop SSIM of 0.9390 against the capture's measured 0.9517 on `rrect-md`, so the
reconstruction is not faithful enough in the band for its SSIM to be quoted as a prediction; the
standard deviation, whose control agrees to 0.3%, is.

### 9.4 The probe fit with the transmission held at vitrea's own

The section 6 fit carried (a, t) free per cell. Re-run on the 2x probe with `a` free and **t fixed at
vitrea's own** — 0.488 / 0.487 / 0.464 / 0.452 / 0.447 by span, measured from vitrea's own captures at
pitch 16 and carried to the other pitches on W9's rule that the level laws are pitch-invariant:

| Δk | −0.10 | 0.00 | +0.10 | +0.20 | +0.25 | **+0.30** | +0.35 | +0.45 | +0.60 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| (a) both σ device | .0610 | .0489 | .0379 | .0292 | .0265 | **.0253** | .0259 | .0303 | .0351 |
| (b) heavy σ device | .0483 | .0395 | .0320 | .0270 | **.0259** | .0259 | .0271 | .0311 | .0351 |

Best: **Δk +0.30** (fit 0.0253, holdout 0.0198) for (a) and **+0.25** (0.0259, holdout 0.0198) for (b).

**Reading — Δk does not go to zero, and the two criteria disagree.** Holding the transmission at
vitrea's own lowers the best Δk from section 8's 0.35 to 0.25–0.30, not to 0. So the 0.35 was not
purely fitting the reference's higher transmission; most of it survives the correction. But the
number that optimises the whole pitch axis (0.25–0.30) is not the number that puts the pitch-16
retained structure nearest native (0.10, §9.3), and the two can be told apart: the higher Δk is
bought at pitch 8, where a narrow kernel over-retains contrast the 2x reference has erased
(section 8's 1.4–1.5× ratios), and it is paid for at pitch 16, which is the pitch every canonical
texture row is scored on. A declaration that wants the canonical rows should take the pitch-16
number; a declaration that wants the material to be right across the frequency axis should take the
other, and accept the canonical rows moving less.

### 9.5 The band

The measured G3 capture's SSIM against native, split into the §5.41 box, the band (0–24 CSS px inside
the contour, outside that box) and the outside — the referee's split, reproduced here from the
captures:

| cell | region | n | main | G3 | Δ | share of the whole-crop loss |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` | whole | 245700 | 0.9517 | 0.9451 | −0.0066 | 100% |
| | box | 26880 | 0.9579 | 0.9330 | −0.0249 | 41.6% |
| | **band < 24** | 33184 | 0.9276 | 0.8983 | **−0.0293** | **60.5%** |
| | outside | 185636 | 0.9550 | 0.9552 | +0.0002 | −2.0% |
| `rrect-ml` | whole | 245700 | 0.9158 | 0.9041 | −0.0117 | 100% |
| | box | 50320 | 0.9590 | 0.9493 | −0.0097 | 17.0% |
| | **band < 24** | 55912 | 0.9395 | 0.8996 | **−0.0399** | **77.3%** |
| | outside | 133500 | 0.8878 | 0.8880 | +0.0002 | −0.8% |
| `rrect-lg` | whole | 245700 | 0.9113 | 0.9078 | −0.0034 | 100% |
| | box | 78016 | 0.9778 | 0.9817 | +0.0039 | −35.9% |
| | **band < 24** | 71640 | 0.9381 | 0.9241 | **−0.0140** | **118.2%** |
| | outside | 70460 | 0.7916 | 0.7919 | +0.0003 | −2.2% |

**Reading.** The band carries 60%, 77% and 118% of the whole-crop loss — on `rrect-lg` more than all
of it, because the interior box actually *improved* (+0.0039) while the band fell. Only one candidate
has a capture, so this is one row per cell and not a sweep; what it establishes for the next
declaration is the budget. The band is 13–29% of the crop's pixels and it moves 2–4× as far as the
box does when the body changes, because the lens samples the body at the refracted position, so a
body change is a band change of roughly three times the size. **A candidate that is chosen on
interior evidence alone can lose the whole-crop row it was chosen to win**, which is what happened
here: on `rrect-lg` the box went the predicted way and the row still fell.

### 9.6 What the declaration should carry — revised again

1. **Do not re-declare on this evidence yet.** §9.2 shows the G3 build did not render the kernel it
   declared: the same nominal law implies a transmission of 0.19–0.37 on the G3 capture against
   0.45–0.49 on `main`, where vitrea's transmission is not a thing the body law changes, and the same
   gap reappears as a 42–77% over-prediction of retained structure. Until that is explained — the
   mip-based body is the first place to look, since a σ halved in device pixels is a different chain
   level and one level's footprint is not the nominal Gaussian — a new Δk fitted on captures the
   implementation cannot reproduce would be fitting the wrong thing.
2. **If the implementation is made to render the declared kernel, the number to declare is Δk ≈ 0.10,
   not 0.35**, with both σ read in device pixels and every other landed constant held. It puts the
   pitch-16 retained structure on the three large spans at 0.1218 / 0.1026 / 0.0866 against native
   0.1273 / 0.1023 / 0.0819, where `main` sits at 0.0975 / 0.0753 / 0.0539 — the first candidate in
   this wave that moves the compare's own frosting reading most of the way to the reference on the
   cells the matrix scores.
3. **Budget the band.** Any body change must be predicted in the band as well as the box; §9.5 puts
   the band's share of the whole-crop movement at 60–118%, and section 8's dry run — box only —
   is therefore not sufficient evidence for a landing decision on its own. The band's own prediction
   needs the lens re-read against the *new* body (the G2 instrument of section 5 over a candidate
   capture), which needs a capture, which is the landing worker's.
4. **Does the transmission itself need a scale term the body cannot provide?** On this evidence,
   **yes, and it is small.** The reference's own transmission on the same column is higher than
   vitrea's at 2x by a ratio of 0.806 / 0.877 / 0.922 on md / ml / lg (t_vitrea ÷ t_ref), while at 1x
   the same ratio is 0.933 / 1.061 / 1.159 — vitrea already matches or exceeds the reference at 1x
   and falls short of it at 2x, on the same constants. A body law cannot supply that: it redistributes
   structure between two widths at a fixed transmission. It also cannot be a plain alpha change,
   because §4 measured the interior *mean* as scale-invariant to 0.0021 on exactly these cells, and
   an alpha that lifted the 2x transmission would move the mean unless the tint level moved with it.
   **The measurement that would establish it** is the W9 response-curve read (§5.34) repeated at 2x
   on the probe's solid and lc16 families: fit the level law `mean = f(backdrop)` and the transmission
   `t = ∂mean/∂backdrop` separately at both scales on backdrops of several linear levels, which
   separates "the material passes more of the backdrop's variation" from "the material sits at a
   different level". The probe already has the four cells that read it — `light-solid`,
   `mid-dark-solid`, `dark-solid` and `checkerboard-lc16` at both scales — and it needs no new
   capture.
