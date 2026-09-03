# W13 G0 — the reference's depth ramp, the small-span heavy width, the dot (2026-09-03)

**What was run, on what.** The windowed instrument of `g0-instrument.md` — the two-component
body under `main`'s landed lens, one heavy share per 4 CSS px depth window, the two widths
pinned — on the two committed probe beds (the 1x W9 probe, `results/2026-09-02-w9-probe/`;
the 2x W12 probe, `results/2026-09-03-w12-lens/probe-2x/`), five spans, pitches 16 / 32 / 64
pooled, with pitches 8 and 4 run separately as checks. Beside it: `g3lib`'s pooled
two-component kernel fit on the deep interior for the heavy width per span; the impulse cells
at both scales and both colour schemes; and the band-windowed SSIM rows on the W12 close bed.
Nothing was captured and no constant under `packages/*/src` was changed. Scripts `g0_ramp.py`,
`g0_smallspan.py`, `g0_impulse.py`, `g0_band.py`; tables under `parts/`; figures
`g0-ramp.png`, `g0-ramp-absolute.png`, `g0-impulse.png`.

**Contract X4 travels with every table below.** The same instrument, on the same geometry, on
vitrea's own captures where the share is one number per span: k(u) flat to **0.012–0.046** at
every span and both scales, and flat to 0.007–0.118 across a whole grid of assumed widths
(`g0-instrument.md` §4, §5, §5b). Its **level** is right to 0.008 on `rrect-md` and biased by
0.07–0.12 on the other spans, because vitrea's canonical bed offers one spatial frequency;
the reference readings below pool three pitches, where the estimator's own error on a
synthetic ramp is 0.003.

## 1. The reference's sharp share by depth

s(u) = 1 − k(u), the share of the transmitted backdrop that comes through the sharp component.
Widths as §5.55 §1 measured them: 1x a 4 CSS px box core and σ 9 device px base; 2x σ 0.5 CSS
px core and σ 9 device px base. Windows are 4 CSS px wide; u is the window's centre in CSS px.
The window at u = 2 is printed but not read (the rim highlight is not in the body model).

**1x** (residual RMS in linear luminance; the fitted transmission is the mean over line sets):

| cell | RMS | t | u 2 | 6 | 10 | 14 | 18 | 22 | 26 | 30 | 34 | 38 | 42 | 46 | 50 | 54 | 58 | 62 | 66 | 70 | 74 | 78 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` (32) | .0055 | .456 | .637 | .621 | .600 | .544 | | | | | | | | | | | | | | | | |
| `capsule-button` (44) | .0074 | .355 | .680 | .642 | .642 | .629 | .607 | .580 | | | | | | | | | | | | | | |
| `rrect-md` (96) | .0176 | .494 | .462 | **.512** | .590 | .570 | .579 | .536 | .513 | .497 | .469 | .431 | **.409** | .388 | | | | | | | | |
| `rrect-ml` (128) | .0139 | .466 | .407 | **.501** | .575 | .543 | .525 | .501 | .489 | .459 | .435 | .414 | .375 | .365 | .340 | .300 | **.288** | .261 | | | | |
| `rrect-lg` (160) | .0126 | .418 | .300 | **.410** | .466 | .464 | .471 | .445 | .437 | .416 | .378 | .361 | .362 | .305 | .285 | .269 | .258 | .225 | .182 | .154 | **.150** | .119 |

**2x**:

| cell | RMS | t | u 2 | 6 | 10 | 14 | 18 | 22 | 26 | 30 | 34 | 38 | 42 | 46 | 50 | 54 | 58 | 62 | 66 | 70 | 74 | 78 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` (32) | .0052 | .412 | .483 | .474 | .439 | .377 | | | | | | | | | | | | | | | | |
| `capsule-button` (44) | .0088 | .345 | .480 | .437 | .412 | .430 | .390 | .362 | | | | | | | | | | | | | | |
| `rrect-md` (96) | .0220 | .519 | .076 | **.192** | .307 | .261 | .264 | .206 | .207 | .146 | .113 | .106 | **.075** | .036 | | | | | | | | |
| `rrect-ml` (128) | .0161 | .485 | −.009 | **.179** | .243 | .185 | .157 | .201 | .156 | .082 | .067 | .073 | .004 | −.047 | −.071 | −.164 | **−.143** | −.168 | | | | |
| `rrect-lg` (160) | .0173 | .405 | −.108 | **.141** | .341 | .334 | .347 | .233 | .094 | .057 | .060 | .006 | .014 | −.057 | −.118 | −.147 | −.187 | −.208 | −.401 | −.450 | **−.247** | −.294 |

Bold: the first and the last window inside the validated range 4 ≤ u ≤ span/2 − 4.

**Read off** (start = the first validated window; reach = where a straight line through the
validated windows crosses zero; floor = the last validated window):

| cell | start s | peak s (at u) | last s (at u) | linear R² | reach, CSS px | reach ÷ (span/2) |
| --- | --- | --- | --- | --- | --- | --- |
| `capsule-button` 1x | 0.642 | 0.642 (10) | 0.629 (14) | 0.72 | 416 | 18.9 |
| `rrect-md` 1x | 0.512 | 0.590 (10) | 0.409 (42) | 0.71 | 144 | 2.99 |
| `rrect-ml` 1x | 0.501 | 0.575 (10) | 0.288 (58) | 0.93 | 115 | 1.79 |
| `rrect-lg` 1x | 0.410 | 0.471 (18) | 0.150 (74) | 0.92 | 108 | 1.35 |
| `capsule-button` 2x | 0.437 | 0.437 (6) | 0.430 (14) | 0.08 | 484 | 22.0 |
| `rrect-md` 2x | 0.192 | 0.307 (10) | 0.075 (42) | 0.72 | 59 | 1.23 |
| `rrect-ml` 2x | 0.179 | 0.243 (10) | −0.143 (58) | 0.91 | 41 | 0.64 |
| `rrect-lg` 2x | 0.141 | 0.347 (18) | −0.247 (74) | 0.88 | 39 | 0.49 |

Four things the tables say.

1. **There is a ramp, and it is large.** On the three thick spans s falls by 0.10 to 0.26
   between the first and the last validated window at 1x (0.512 → 0.409, 0.501 → 0.288,
   0.410 → 0.150), and by 0.12 to 0.39 at 2x — five to twenty times the instrument's own
   flat-field spread on vitrea (0.012–0.046).
2. **It is not a ramp to zero at the centre.** At 1x the linear extrapolation crosses zero at
   108 / 115 / 144 CSS px on `rrect-lg` / `-ml` / `-md`, which is 1.35 / 1.79 / 2.99 half-spans
   — i.e. **closer to a common absolute depth than to a fixed fraction of the span**
   (`g0-ramp-absolute.png` shows the same readings against absolute u, where the three thick
   spans lie much nearer one curve than they do against u/(span/2)). At 1x the practical
   consequence is a floor: a 96-point surface still carries s ≈ 0.39–0.41 at its centre.
3. **The scale changes the start much more than the shape.** At 2x the ramp starts at 0.14–0.19
   on the thick spans against 0.41–0.51 at 1x, and reaches zero at 39–59 CSS px against
   108–144. §5.55 §2's "at 2x it starts lower and reaches zero sooner" is confirmed and
   quantified. The two thin spans move much less (`rrect-sm` 0.62 → 0.47, capsule 0.64 → 0.44
   at the same window), so the scale term is not one multiplier on s.
4. **On the thin spans there is barely a ramp at all** over the depths that exist. Across
   every printed window, including the excluded first one, `rrect-sm` (half-span 16) falls
   0.637 → 0.544 at 1x and 0.483 → 0.377 at 2x, and `capsule-button` (half-span 22) falls
   0.680 → 0.580 and 0.480 → 0.362 — a tenth of a unit over the whole shape, from a much
   higher start than the thick spans have anywhere. The reference's small surfaces are
   mostly sharp at both scales; vitrea's `sizeScatterFloor` 0.4 gives them a sharp share of
   0.60 / 0.595, which at 1x is nearly right and at 2x is 0.13–0.16 too high.

**Where the 2x reading breaks.** On `rrect-ml` and `rrect-lg` at 2x, s goes **negative** in
the deep windows (to −0.17 and −0.45). A mix cannot have a negative weight; what the fit is
saying is that the reference's deep interior at 2x on the large spans is **blurrier than the
σ 4.5 CSS px base the model was given** — negative sharp weight is how a two-component model
with too narrow a base manufactures extra attenuation. Repeating the fit with k held inside
[0, 1] costs 0.0006 (`-ml`) and 0.0018 (`-lg`) of RMS on 0.016–0.017 and gives s reaching
exactly 0 at the centre:

| cell | s, first validated window → last, k bounded to [0, 1] | RMS bounded / free |
| --- | --- | --- |
| `rrect-md` 2x | 0.192 → 0.075 (unchanged; the bound never binds) | 0.02201 / 0.02201 |
| `rrect-ml` 2x | 0.199 → 0.000 | 0.01668 / 0.01611 |
| `rrect-lg` 2x | 0.195 → 0.000 | 0.01909 / 0.01733 |

§4 asks the width question the negative windows raise directly.

**The pitch checks.** Pitch 8 at 1x agrees on the level and carries little depth information
(`rrect-md` s 0.434 → 0.447, `rrect-lg` 0.413 → 0.351). Pitch 8 at **2x** is unusable and was
excluded from the primary reading for a stated reason: the fitted transmission is +0.09 on
`rrect-md` and **−0.11** on `rrect-lg` — the reference passes essentially nothing at that
pitch and what it does pass is anti-correlated with the plate, the inversion §5.55 §3
recorded. Pitch 4 is at the identifiability ceiling on every cell (§5.55 §6) and its readings
are in `parts/g0-ramp.json` only. Adding pitch 8 to the pool moves the 2x `rrect-md` reading
by up to 0.03 per window and the 1x readings by up to 0.06.

**Sensitivity to the assumed widths.** Over a 20-point grid of both widths, taking the five
best points by RMS: `rrect-md` 1x s(first) 0.479–0.523 and s(last) 0.373–0.409; `rrect-lg` 1x
0.368–0.460 and 0.087–0.150; `rrect-md` 2x 0.043–0.252 and −0.114–0.113; `rrect-lg` 2x
0.126–0.236 and −0.309–−0.100. The **shape** survives; the **2x absolute values** do not,
which is the same limit `g0-instrument.md` §5 recorded, made worse at 2x because the two
components' widths are closer together there.

## 2. H1 against H2

- **H1**, the layer tree's opacity ramp read literally (§5.50 §2: opacity 0.5 at u = 1 rising
  to 1 at u = span/2, the same inputs at both scales): s = 0.5 · max(0, 1 − u/(span/2)).
- **H2**, a ramp with a free start, reach and floor: s = s₀ · max(0, 1 − u/(ρ·span/2)) + floor.

RMS over the validated windows, in units of s:

| cell | **H1** | H2 shared over spans at this scale | H2 per span (s₀ / ρ / floor) | H2 per span RMS |
| --- | --- | --- | --- | --- |
| `capsule-button` 1x | 0.372 | — | 0.137 / 3.97 / 0.516 | 0.003 |
| `rrect-md` 1x | 0.272 | — | 0.327 / 1.60 / 0.286 | 0.031 |
| `rrect-ml` 1x | 0.192 | — | 0.572 / 1.69 / 0.034 | 0.023 |
| `rrect-lg` 1x | **0.094** | — | 0.542 / 1.37 / −0.008 | 0.030 |
| **all four, 1x** | — | **0.093** (s₀ 0.559, ρ 1.650, floor 0.035) | — | — |
| `capsule-button` 2x | 0.170 | — | 0.077 / 3.90 / 0.358 | 0.010 |
| `rrect-md` 2x | **0.093** | — | 0.360 / 1.39 / −0.043 | 0.038 |
| `rrect-ml` 2x | 0.188 | — | 0.447 / 0.93 / −0.142 | 0.038 |
| `rrect-lg` 2x | 0.287 | — | 0.594 / 0.76 / −0.200 | 0.099 |
| **all four, 2x** | — | **0.141** (s₀ 0.584, ρ 0.976, floor −0.200) | — | — |

Readings:

- **H1 is rejected everywhere except `rrect-lg` at 1x and `rrect-md` at 2x**, and those two
  are coincidences of opposite sign — at 1x H1 is too steep on the small and medium spans and
  right on the largest; at 2x it is far too shallow on the largest and right on the medium.
  One law of the form "0.5 falling to 0 at the centre, the same at both scales" cannot be the
  reference's; the layer tree's opacity inputs are what the filter is *given*, not what the
  material does with them at the pixel.
- **H2 shared over the spans at one scale is as good as H1's best cell and much better than
  H1's worst** (0.093 against 0.094–0.372 at 1x; 0.141 against 0.093–0.287 at 2x), and its
  fitted ρ says the same thing the reach column did: **1.65 half-spans at 1x, 0.98 at 2x**.
  The scale moves the reach by 1.7×, and it moves the start much less (s₀ 0.559 → 0.584).
- **H2 fitted per span is a good fit everywhere** (0.003–0.099) but its constants do not lie
  on any simple span law — ρ 1.60 / 1.69 / 1.37 at 1x with floors 0.29 / 0.03 / −0.01. Read
  together with §1's reach column, the honest summary is that **s is closer to a function of
  absolute depth than of u/(span/2)**, and a per-span (s₀, ρ, floor) is that absolute
  function re-expressed three times. G1's first job is to test an absolute-depth form
  directly — H2 with ρ·span/2 replaced by one length in CSS px — which this round did not
  score and which the reach column predicts will beat both.
- The 2x shared fit's floor runs to its lower bound (−0.200), which is the negative-window
  artefact of §1 leaking into the form; the bounded reading (s → 0 at the centre) is the one
  a declaration should be fitted against.

## 3. Where §5.55 §2's numbers sit in this reading

§5.55 §2 reported the sharp component's amplitude by depth from windows that **started at
u 20** and did not see the band: `rrect-lg` 1x 0.169 at u 20–28 falling to 0.040 at u 76–80,
and `rrect-md` 2x pitch 32 0.094 → 0.067 → 0.018 → 0.000 over u 20 → 48 with the heavy share
0.82 → 1.00. Those are *amplitudes* (transmission × share), this document's s(u) is the
*share*. Converted with this round's fitted transmissions: `rrect-lg` 1x amplitude
t·s = 0.418 · 0.445 = 0.186 at u 22 falling to 0.418 · 0.119 = 0.050 at u 78, against §5.55's
0.169 → 0.040; `rrect-md` 2x 0.519 · 0.206 = 0.107 at u 22 falling to 0.519 · 0.036 = 0.019
at u 46, against 0.094 → 0.000. The two readings agree to about 10% of the amplitude over
the depths §5.55 covered. **What this round adds is the band**: over 4 ≤ u < 20, which §5.55
never measured, s rises to its peak and then falls, and at 2x it is 0.14–0.19 at u 6 rather
than the 0.5 the layer tree's ramp would put there.

## 4. The heavy width per span

Two readings of the same question, because they disagree with each other and both are on the
record.

**(a) The pooled two-component fit on the deep interior** (`g3lib.fit_two_joint`, the
estimator §5.55 §1 used, σ_heavy swept in **device** px with σ_sharp free, pitches 8 / 16 /
32 / 64). The layer tree's radius law floors at 4/3 buffer px on every span below 48, and one
buffer pixel is four device px, so its prediction for `rrect-sm` and `capsule-button` is
**5.33 device px at both scales**.

| cell | best σ_heavy, device px | σ_sharp, CSS px | heavy share | RMS | RMS at 5.33 | RMS at 9.0 |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` 1x | 12.0 | 1.25 | 0.550 | 0.0164 | 0.0350 | 0.0197 |
| `capsule-button` 1x | 7.0 (flat 5–10) | 1.25 | 0.144 | 0.0184 | 0.0186 | 0.0185 |
| `rrect-md` 1x | 9.0 | 1.25 | 0.503 | 0.0136 | 0.0220 | 0.0136 |
| `rrect-ml` 1x | 9.0 | 1.25 | 0.621 | 0.0146 | 0.0243 | 0.0146 |
| `rrect-lg` 1x | 9.0 | 1.00 | 0.756 | 0.0170 | 0.0270 | 0.0170 |
| `rrect-sm` 2x (all pitches) | 12.0 | 0.75 | 0.680 | 0.0216 | 0.0456 | 0.0278 |
| `rrect-sm` 2x (§5.53's settled cells excluded) | **9.0** | 0.75 | 0.531 | 0.0112 | 0.0159 | 0.0112 |
| `capsule-button` 2x | 8.0 | 0.50 | 0.637 | 0.0120 | 0.0180 | 0.0126 |
| `rrect-md` 2x | 8.0 | 0.25 | 0.966 | 0.0154 | 0.0350 | 0.0164 |
| `rrect-ml` 2x | 9.0 | 1.50 | 1.000 | 0.0164 | 0.0447 | 0.0164 |
| `rrect-lg` 2x | 11.0 | 0.50 | 1.000 | 0.0160 | 0.0427 | 0.0200 |

The three large spans at 1x reproduce §5.55 §1 exactly (σ 9 device px, shares 0.503 / 0.621 /
0.756 against §5.38 §3's 0.555 / 0.662 / 0.764), which is the check that the estimator is the
published one. **The small spans do not read 5.33 device px.** `rrect-sm` reads 9–12 and
`capsule-button` 7–8, and 5.33 costs 40–180% of RMS on every cell except the capsule at 1x,
where the heavy component's own weight is 0.144 and the sweep is flat from 5 to 10 device px
— unidentified, not equal. The 2x `rrect-sm` row moves from 12.0 to 9.0 when §5.53's three
frequency-settled cells (`checkerboard-8`, `checkerboard-64`, `checkerboard-lc16` on
`rrect-sm`) are dropped, and the RMS halves; the settled-excluded row is the one to read.

**Finding: the layer tree's `inputBlurRadius` floor of 4/3 buffer px is not a Gaussian σ of
5.33 device px at the pixel.** Either Apple's radius is not a σ (a "blur radius" of r
buffer px behaving like σ ≈ 1.5–2 r is entirely ordinary), or the small spans' base is not the
radius law's. Either way, **the probe does not ask for a span term on σ_heavy**: 8–12 device
px covers every span at both scales, against the one number 9 that §5.55 §1 already declared.

**(b) The windowed instrument, with the ramp free underneath the width.** The same question
asked where the ramp is modelled rather than averaged into the fit:

| cell | radius law, CSS px | best σ_heavy by RMS | s first → last there | σ_heavy at the radius law × 1.0 → s first → last |
| --- | --- | --- | --- | --- |
| `rrect-md` 1x | 9.90 | 9.0 (rms .0176) | 0.512 → 0.409 | 9.90 (.0177) → 0.505 → 0.407 |
| `rrect-ml` 1x | 12.95 | 9.0 (.0139) | 0.501 → 0.288 | 12.95 (.0163) → 0.449 → 0.302 |
| `rrect-lg` 1x | 16.00 | **8.0** (.0122) | 0.421 → 0.121 | 16.00 (not in the top four) |
| `rrect-md` 2x | 4.95 | 3.71 (.0216) | 0.147 → −0.021 | 4.95 (.0226) → 0.212 → 0.105 |
| `rrect-ml` 2x | 6.48 | 4.50 (.0161) | 0.179 → −0.143 | 6.48 (.0213) → 0.196 → **+0.020** |
| `rrect-lg` 2x | 8.00 | 4.50 (.0173) | 0.141 → −0.247 | 8.00 (.0221) → 0.239 → **+0.034** |

This is where the two readings pull apart and it matters for G1. By RMS the windowed fit
prefers a **narrow** base at 2x (4.5 CSS px = 9 device px) and pays for it with impossible
negative shares deep inside; the radius law's own width (8 CSS px = 16 device px on
`rrect-lg`) makes the shares physical everywhere at a 28% RMS cost. The deep-interior fit (a)
on the same cell prefers 11 device px. **The 2x base width on the large spans is not settled
by this round**: 9 to 16 device px are all defensible on some estimator, and the ramp's 2x
floor moves from −0.25 to +0.03 across that range. That is the single largest uncertainty in
these tables and G1 should not declare a 2x ramp floor without closing it.

## 5. The impulse cells, and the dot

The `impulse` backdrop is a 5 × 3 grid of 4 × 4 CSS px white dots on black, 64 CSS px apart.
Exactly **one** dot falls under `capsule-button`, at (159.5, 103.5) — SDF depth 18.5 CSS px on
a span of 44, so u/(span/2) = 0.84. Three fall under `rrect-md`; the middle one sits at depth
44.5 on a span of 96, the outer two at 15.5 and 16.5.

Peak linear luminance within 6 CSS px of the dot minus the median of the surround (an annulus
26–34 CSS px away, inside the silhouette):

| cell | depth | reference | vitrea | **vitrea ÷ reference** |
| --- | --- | --- | --- | --- |
| `capsule-button` 1x light | 18.5 | 0.0066 | **0.0000** | **0.00** |
| `capsule-button` 1x dark | 18.5 | 0.0066 | **0.0000** | **0.00** |
| `capsule-button` 2x light | 18.2 | 0.0266 | **0.0000** | **0.00** |
| `capsule-button` 2x dark | 18.2 | 0.0266 | **0.0000** | **0.00** |
| `rrect-md` 1x light, centre dot | 44.5 | 0.0565 | 0.1351 | 2.39 |
| `rrect-md` 1x light, edge dots | 15.5 / 16.5 | 0.0742 | 0.1351 | 1.82 |
| `rrect-md` 2x light, centre dot | 44.2 | 0.0623 | 0.1220 | 1.96 |
| `rrect-md` 2x light, edge dots | 15.8 / 16.2 | 0.1619 | 0.1220 | 0.75 |

**The capsule's dot does not disappear in vitrea — vitrea's capsule shows no backdrop at
all.** Its interior (depth > 4 CSS px) has a standard deviation of exactly **0.00000** on the
impulse scene at both scales and both schemes, at a level of 0.0037 (1x) / 0.0033 (2x), which
is the impulse plate's own global mean (0.00375). The reference's capsule keeps a dot of peak
0.0131 above a surround of 0.0065 at 1x, and 0.033 above 0.0065 at 2x. The two-component read
confirms it from the other side: on the disc about the dot the reference fits a core of σ 2.5
CSS px carrying transmission 0.025, vitrea fits **0.000 and 0.000**.

The backdrop-by-backdrop table says this is the impulse scene and not the thin material
generally (interior mean / standard deviation, depth > 4 CSS px, 1x):

| backdrop | plate mean | plate σ | capsule reference | capsule vitrea | `rrect-md` reference | `rrect-md` vitrea |
| --- | --- | --- | --- | --- | --- | --- |
| `impulse` | 0.0037 | 0.0611 | 0.0066 / 0.00068 | 0.0037 / **0.00000** | 0.4310 / 0.00856 | 0.4639 / 0.01068 |
| `dark-solid` | 0.0117 | 0 | 0.0110 / 0 | 0.0117 / 0 | 0.4797 / 0 | 0.4952 / 0.00264 |
| `checkerboard` | 0.5000 | 0.5000 | 0.6129 / 0.13577 | 0.6738 / 0.11579 | 0.6792 / 0.11093 | 0.6922 / 0.09454 |
| `hc-text` | 0.7400 | 0.4386 | 0.6538 / 0.11374 | 0.7420 / 0.10777 | 0.7313 / 0.10631 | 0.7477 / 0.09261 |
| `photo` | 0.2141 | 0.1220 | 0.5753 / 0.03427 | 0.6109 / 0.03386 | 0.6612 / 0.05353 | 0.6553 / 0.03884 |

Three things follow.

1. **The dot gap is not the heavy width.** §4 measured the reference's own base on the small
   spans at 7–12 device px against vitrea's 10 CSS px = 10 device px at 1x; that is close,
   and it cannot turn a visible dot into a standard deviation of exactly zero. Nor is it the
   sharp share of §1: vitrea's capsule sharp share is 0.595 against the reference's 0.62–0.64
   at 1x, which if anything favours vitrea.
2. **On the same scene under the thick `rrect-md`, vitrea's dot is 1.8–2.4× too strong at 1x**
   and 0.75× too weak at 2x on the near-edge dots — the interior being too sharp at 1x and the
   2x band being where the widths and the ramp fight, both consistent with §1.
3. **What the capsule's zero is** is not settled by this round. vitrea renders the impulse
   capsule at exactly the backdrop's global mean with no spatial structure, which is what a
   group that resolved to no sampling (`backdrop = 0`, the output being the adaptive tint
   alone) or to a fully occluded thin material over a near-black backdrop would produce. The
   distinguishing evidence is in the compare's own `report__webgpu.json` for that cell
   (the resolved `GlassGroupState`), which this analysis did not read. It is a
   **level/sampling** question on the thin material over a dark backdrop, not a body-mix one,
   so on the charter's own terms the dot gap **returns to W12's Deferred shape** — with a
   sharper description than it had: "vitrea shows no backdrop structure at all under
   `impulse__capsule-button`, at four profiles".

## 6. Contract X6 — the band-windowed rows, on the W12 close bed

`ssimBand` and `ssimInterior`: the compare's own SSIM statistic (`w11lib.ssim_map`, the pinned
replica of `src/metrics/perceptual.ts`) averaged inside the silhouette, split at a fixed depth
of **24 CSS px** from the contour. Recorded here as the baseline; no bound is adopted at G0.

| cell | whole silhouette | **band** (u < 24) | **interior** (u ≥ 24) | band px | interior px |
| --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-sm` 1x | 0.9673 | 0.9673 | — | 2 000 | 0 |
| `checkerboard__capsule-button` 1x | 0.8815 | 0.8815 | — | 4 872 | 0 |
| `checkerboard__rrect-md` 1x | 0.9485 | 0.9303 | 0.9813 | 9 648 | 5 376 |
| `checkerboard__rrect-ml` 1x | 0.9580 | 0.9356 | 0.9802 | 13 972 | 14 076 |
| `checkerboard__rrect-lg` 1x | 0.9598 | 0.9386 | 0.9745 | 17 916 | 25 900 |
| `photo__rrect-md` 1x | 0.9926 | 0.9908 | 0.9958 | 9 648 | 5 376 |
| `photo__rrect-lg` 1x | 0.9941 | 0.9916 | 0.9959 | 17 916 | 25 900 |
| `hc-text__rrect-md` 1x | 0.9200 | 0.8938 | 0.9670 | 9 648 | 5 376 |
| `checkerboard__rrect-sm` 2x | 0.9417 | 0.9417 | — | 7 980 | 0 |
| `checkerboard__capsule-button` 2x | 0.8632 | 0.8632 | — | 19 468 | 0 |
| `checkerboard__rrect-md` 2x | 0.9412 | 0.9312 | 0.9592 | 38 560 | 21 504 |
| `checkerboard__rrect-ml` 2x | 0.9491 | 0.9395 | 0.9586 | 55 912 | 56 288 |
| `checkerboard__rrect-lg` 2x | 0.9594 | 0.9381 | 0.9741 | 71 640 | 103 600 |
| `photo__rrect-md` 2x | 0.9944 | 0.9928 | 0.9973 | 38 560 | 21 504 |
| `photo__rrect-lg` 2x | 0.9955 | 0.9924 | 0.9976 | 71 640 | 103 600 |
| `hc-text__rrect-md` 2x | 0.9432 | 0.9284 | 0.9696 | 38 560 | 21 504 |

Two notes for whoever adopts these as bounds. **The split at 24 CSS px leaves `rrect-sm` and
`capsule-button` with no interior at all** — their half-spans are 16 and 22 — so `ssimBand`
on those two cells is the whole-silhouette row under another name and `ssimInterior` is
undefined; the schema needs to say so rather than emit a NaN. And these numbers are inside the
silhouette, where the compare's published `ssimMean` is over the whole cell crop including the
shadow and the page outside it; the band row is 0.01–0.03 below the whole-silhouette row on
every checkerboard cell, which is the split doing its job — the band is where the error is.

## 7. What the declaration should carry

Findings, with the evidence, not decisions.

- **There is a depth ramp on the sharp share and it is the dominant unmodelled term in the
  band.** It falls by 0.10–0.26 (1x) and 0.12–0.39 (2x) across the depths this instrument can
  read, against a flat-field noise of 0.012–0.046 on the same instrument on vitrea's own
  captures. Nothing in these tables supports a uniform share.
- **The layer tree's literal ramp (H1) is not the law.** It is right on exactly one cell per
  scale and wrong by 0.17–0.37 on the others (§2). A declaration that adopts §5.50 §2's
  "0.5 at the edge → 0 at the centre, the same inputs at both scales" as a form will land the
  wrong shape on three of five spans.
- **The reach looks absolute, not proportional.** 1.35 / 1.79 / 2.99 half-spans on lg / ml /
  md at 1x is 108 / 115 / 144 CSS px — a spread of 1.3× in absolute depth against 2.2× in
  relative depth. The first form G1 should score, which this round did not, is
  s = s₀ · max(0, 1 − u/U) + floor with **U a length in CSS px** and a scale term on U;
  H2's per-span constants (§2) are a re-expression of that and fit every span to 0.003–0.099.
- **The scale moves the start and the reach, and moves them differently on thin and thick
  spans.** Thick: start 0.41–0.51 → 0.14–0.19, reach 108–144 → 39–59 CSS px. Thin: start
  0.62–0.64 → 0.44–0.47, and the span is too short for a reach to be measured. One multiplier
  on s₀ will not carry this; one multiplier on U plus a smaller one on s₀ might, and the two
  thin spans are the cells that discriminate them.
- **The 2x base width on the large spans is the biggest open number**, and it sits underneath
  the ramp's 2x floor. σ 9 device px (§5.55 §1, best by RMS in the windowed fit) forces
  physically impossible negative sharp shares of −0.17 to −0.45 deep inside `rrect-ml` and
  `-lg`; the layer tree's own radius law (16 device px on `rrect-lg`) makes every share
  physical at a 28% RMS cost; the deep-interior fit prefers 11. Until that is closed the 2x
  ramp's floor is only bounded to 0.00 ≤ floor ≤ 0.03, not measured.
- **The transmission was assumed constant with depth.** The instrument has a mode that frees
  it per window and is identified on the pooled pitches (`g0-instrument.md` §1). It was not
  exercised in these tables. If the reference's transmission ramps, part of what §1 reports
  as a share ramp is a transmission ramp, and the two land as different shader terms. This is
  the cheapest single check available to G1 and it should run before a form is fitted.
- **The probe does not ask for a span term on σ_heavy.** 8–12 device px covers every span at
  both scales (§4a) and the radius law's floored 5.33 device px is rejected on the small spans
  by 40–180% of RMS. §5.56 §1's one number stands; a span term would be fitting the estimator.
- **The dot gap is not a body-mix gap.** vitrea renders zero backdrop structure under
  `impulse__capsule-button` at four profiles (§5). That is a sampling or level defect on the
  thin material over a near-black backdrop and it wants a `GlassGroupState` read, not a
  material constant. It should leave this wave's declaration and become its own item.
- **The band rows are ready to record and their definition needs one amendment**: the 24 CSS
  px split leaves the two small spans with no interior window (§6).

## For claims §5.60

*Draft. Numbers and tables in the ledger's style; the section is written for the wave's
recorder to place, not adopted here.*

### 5.60 W13 G0: the reference's sharp share ramps in depth, the ramp's reach is a length and not a fraction of the span, and the dot gap is not the body (2026-09-03)

The measurement W13's charter opened with, run on the two committed probe beds by an
instrument first proven on vitrea's own captures. W12 G0's warp-recovery model with the lens
**pinned** at `main`'s landed law (W12 G2's power form, ω 0.8) and the body's mix free per
4 CSS px depth window; the model is bilinear at fixed widths and is solved by alternating
least squares, no optimiser and no penalty. Nothing here is a capture or a fit into the
product; the document, JSON and scripts are `results/2026-09-03-w13-ramp/g0/`.

#### 1. The instrument, and what it recovered from a known law (contract X4)

| acceptance | result |
| --- | --- |
| the analytic plate against the committed raster, 140 line sets, both scales | **0.00000000** |
| the estimator on a synthetic known k(u), pitches 16/32/64 (the reference's configuration) | **0.003** flat, **0.007** ramped |
| the same at one pitch (vitrea's canonical bed) | 0.26 flat, 0.37 ramped — **not identified** |
| vitrea `main`, flatness of k(u) over 4 ≤ u ≤ span/2 − 4, four spans × two scales | **0.012–0.046** |
| the same over a 30-point grid of assumed widths | 0.009–0.106 |
| vitrea `main`, level of k: `rrect-md` 1x / 2x | **+0.002 / +0.008** |
| the same, `capsule` / `rrect-ml` / `rrect-lg` (with `photo` pooled) | +0.11 / −0.07 / −0.09 |
| the candidate at `sizeScatterScaleTerm` 0.35, 2x, flatness | **0.024–0.031** |

The level's miss is one mechanism, measured: at one spatial frequency the transmission and a
uniform shift of the share trade against each other (the σ-10 heavy component keeps 0.15 of
the pitch-16 fundamental against the sharp term's 0.97, and the σ-5 one at the candidate's
device-pixel widths keeps 0.62). **The shape of k(u) is identified and its level is not,
wherever only one pitch is available.** Every reference reading below pools three.

#### 2. The reference's sharp share by depth

s(u) = 1 − k(u) per 4 CSS px window, pitches 16 / 32 / 64, the widths of §5.55 §1. First and
last validated window (4 ≤ u ≤ span/2 − 4), the peak, and where a straight line through the
windows crosses zero:

| cell | s at the first window | peak s (u) | s at the last window (u) | reach, CSS px | reach ÷ (span/2) |
| --- | --- | --- | --- | --- | --- |
| `rrect-sm` 1x | 0.621 (u 6) | 0.621 | 0.600 (u 10) | — | — |
| `capsule-button` 1x | 0.642 | 0.642 (10) | 0.629 (14) | 416 | 18.9 |
| `rrect-md` 1x | 0.512 | 0.590 (10) | 0.409 (42) | 144 | 2.99 |
| `rrect-ml` 1x | 0.501 | 0.575 (10) | 0.288 (58) | 115 | 1.79 |
| `rrect-lg` 1x | 0.410 | 0.471 (18) | 0.150 (74) | 108 | 1.35 |
| `rrect-sm` 2x | 0.474 (u 6) | 0.474 | 0.439 (u 10) | — | — |
| `capsule-button` 2x | 0.437 | 0.437 (6) | 0.430 (14) | 484 | 22.0 |
| `rrect-md` 2x | 0.192 | 0.307 (10) | 0.075 (42) | 59 | 1.23 |
| `rrect-ml` 2x | 0.179 | 0.243 (10) | −0.143 (58) | 41 | 0.64 |
| `rrect-lg` 2x | 0.141 | 0.347 (18) | −0.247 (74) | 39 | 0.49 |

Scored against the layer tree's own ramp and against a free one (RMS in units of s over the
validated windows):

| | `capsule` | `rrect-md` | `rrect-ml` | `rrect-lg` | shared over the four |
| --- | --- | --- | --- | --- | --- |
| **H1** s = 0.5·max(0, 1 − u/(span/2)), 1x | 0.372 | 0.272 | 0.192 | **0.094** | — |
| **H2** s = s₀·max(0, 1 − u/(ρ·span/2)) + floor, 1x per span | 0.003 | 0.031 | 0.023 | 0.030 | **0.093** (s₀ 0.559, ρ 1.650, floor 0.035) |
| **H1**, 2x | 0.170 | **0.093** | 0.188 | 0.287 | — |
| **H2**, 2x per span | 0.010 | 0.038 | 0.038 | 0.099 | **0.141** (s₀ 0.584, ρ 0.976, floor −0.200) |

**The ramp is real and large; §5.50 §2's opacity inputs are not its pixel law.** H1 is right
on one cell per scale and wrong by 0.17–0.37 on the rest. H2's reach is 1.65 half-spans at 1x
and 0.98 at 2x, and the per-span reaches in absolute depth (108 / 115 / 144 CSS px at 1x on
lg / ml / md) spread by 1.3× where the relative ones spread by 2.2× — **the reach reads as a
length, not as a fraction of the span**. §5.55 §2's amplitudes are reproduced where they
overlap (`rrect-lg` 1x 0.186 → 0.050 against 0.169 → 0.040; `rrect-md` 2x 0.107 → 0.019
against 0.094 → 0.000); what is new is the band, 4 ≤ u < 20, where s rises to a peak and
where at 2x it is 0.14–0.19 rather than the 0.5 the layer tree would put there.

**Open, and it sits under the 2x floor.** On `rrect-ml` and `-lg` at 2x the free fit answers
with negative sharp shares (−0.17, −0.45), which a mix cannot have; bounding k to [0, 1]
costs 4–10% of RMS and puts s at exactly 0 at the centre. The reason is the base width: by
RMS the windowed fit prefers σ 9 device px there, the layer tree's radius law says 16, and the
deep-interior fit says 11. **The 2x ramp's floor is bounded to 0.00–0.03, not measured.**

#### 3. The heavy width per span — no span term is asked for

Pooled two-component fits on the deep interior (σ_heavy in **device** px, σ_sharp free,
pitches 8/16/32/64) reproduce §5.55 §1 on the three large spans at 1x (9 / 9 / 9, shares
0.503 / 0.621 / 0.756). The small spans read **9–12** (`rrect-sm`; 9 at 2x once §5.53's three
frequency-settled cells are excluded, which halves the RMS) and **7–8** (`capsule-button`,
its heavy weight 0.144 at 1x and the sweep flat from 5 to 10 — unidentified there). The layer
tree's floored radius (4/3 buffer px = **5.33 device px**) costs 40–180% of RMS on every cell
where the width is identified. **§5.56 §1's one number stands; the radius law's floor is not
a Gaussian σ at the pixel**, and the by-eye dot gap is not a small-span width.

#### 4. The dot: vitrea renders no backdrop at all under `impulse__capsule-button`

Peak linear luminance within 6 CSS px of the dot minus the surround, reference | vitrea |
ratio: `capsule-button` **0.0066 | 0.0000 | 0.00** (1x, both schemes) and **0.0266 | 0.0000 |
0.00** (2x, both schemes); `rrect-md` centre dot 0.0565 | 0.1351 | **2.39** at 1x and 0.0623 |
0.1220 | 1.96 at 2x, its near-edge dots 0.1619 | 0.1220 | 0.75 at 2x. vitrea's capsule
interior on that scene has standard deviation **exactly 0.00000** at a level equal to the
plate's own global mean, at all four profiles, while the same capsule over `checkerboard`,
`hc-text` and `photo` carries 0.034–0.116. **The gap is not the body's mix or its widths — it
is that the thin material over a near-black backdrop shows no backdrop structure at all**, a
sampling or level question that wants the cell's resolved `GlassGroupState` read, and it
leaves the ramp's declaration.

#### 5. The band-windowed rows (contract X6), on the W12 close bed

SSIM inside the silhouette split at 24 CSS px from the contour, whole | band | interior:
1x `rrect-md` 0.9485 | 0.9303 | 0.9813, `-ml` 0.9580 | 0.9356 | 0.9802, `-lg` 0.9598 | 0.9386
| 0.9745, `photo__rrect-md` 0.9926 | 0.9908 | 0.9958, `hc-text__rrect-md` 0.9200 | 0.8938 |
0.9670; 2x `rrect-md` 0.9412 | 0.9312 | 0.9592, `-ml` 0.9491 | 0.9395 | 0.9586, `-lg` 0.9594 |
0.9381 | 0.9741, `photo__rrect-md` 0.9944 | 0.9928 | 0.9973, `hc-text__rrect-md` 0.9432 |
0.9284 | 0.9696. `rrect-sm` and `capsule-button` have **no interior window** at this split
(their half-spans are 16 and 22), so their band row is the whole-silhouette row and the
schema must say so rather than emit a NaN.

#### 6. Limits

The lens is fixed by decision, so its 0.6–1.3 px 2x mid-depth residual (§5.55 §4) is inside
every residual here and any depth-correlated part of it is absorbed by the windows near the
band; windows below u = 4 are excluded for that and for the rim. The transmission is assumed
constant with depth — the instrument has a mode that frees it and it was not exercised. The
residual RMS on the reference (0.005–0.023) is two to four times vitrea's on the same
geometry (0.004–0.009): the model is vitrea's body under vitrea's lens and on the reference it
is an approximation. Pitch 8 at 2x is excluded from the primary reading (its fitted
transmission is −0.11 on `rrect-lg`, the inversion §5.55 §3 recorded) and pitch 4 is at the
identifiability ceiling. The 2x levels move with the assumed widths by up to 0.4 in s; the
shapes do not.
