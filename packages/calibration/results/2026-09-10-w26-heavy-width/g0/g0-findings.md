# W26 G0 — the heavy tap as a parameter: findings

**Spike. Deliverable: findings; no material change lands.** The three candidate taps are on this
branch behind one constant each, all inert at their defaults, with the 33 renderer goldens and all
36 re-rendered bed captures byte-identical there. Nothing was fitted; G1 fits.

Evidence in this directory: `chain-kernel.txt` (the pyramid's own kernel, simulated),
`tap-today.txt` (deliverable 1), `mapping.txt` (deliverable 2), `share-at-width.txt`
(deliverable 3's share question), and the scripts that produced each. Read-only on the fixtures and
on the canonical `web-captures/`; every render went to scratch through `--out-matrix` and
`VITREA_WEB_CAPTURES`.

---

## 1. How the heavy sample is taken today — and why the width saturates

The body's deep sample is `clamp(bodyChainLod + log2(gainEff), 0, chainMaxLod)`, and on the bed at
dpr 1 every term of that is now measured rather than inferred:

| quantity | value |
| --- | --- |
| `blurSigma` | 1.25 device px; `bodySigmaCssFor` divides by the ratio → 1.25 CSS px at dpr 1 |
| texels per CSS px | 1.0 — the backdrop raster is 320 × 200 for a 320 × 200 CSS canvas |
| `bodyChainLod` | **1.0589** |
| the chain | 5 levels: 320×200 → 160×100 → 80×50 → 40×25 → 20×12; the next would be 10×6, whose shorter side is under `MIN_LEVEL_EXTENT` = 8 |
| `chainMaxLod` | **4** at dpr 1 (and 5 at dpr 2, where the raster is 640 × 400) |

`bodyChainLod + log2(8)` is **4.0589**. The clamp has therefore been holding since the material was
fitted. Rendered at `sizeScatterGainMax` 4 / 8 / 10.3 / 16 / 32 on the three 1x impulse rows, reader
A returns **the same three widths at 8, 10.3, 16 and 32 to the last digit** (`rrect-md` 9.083,
`-ml` 14.361, `-lg` 19.782) and moves only at gain 4, which asks for level 3.06 and gets it. That
is the ledger's "8 → 10.3 leaves 13.29" reproduced with its cause: **the gain is not a width lever
because the pyramid has no level above the one it already reads**, and `sizeScatterGainMax`,
`sizeScatterGainMax2x` and `sizeScatterGainFar2x` grade a quantity the clamp then discards.

**What filter builds each level, against a Gaussian** (`chain-kernel.txt`, `WGSL_DOWNSAMPLE_PASS`
simulated exactly on a level-0 delta and read back the way `textureSampleLevel` reads it): the
13 taps all land on half-integer positions, so each is an exact 2 × 2 box average and the pass is
the standard bloom downsample. Its second-moment σ reads **1.570 / 3.340 / 6.799 / 13.660 /
27.351** level-0 texels at levels 1…5 — doubling from level 2 on — with **kurtosis −0.23 at every
level**: platykurtic, self-similar, neither a Gaussian (0) nor a box (−1.2), and 12 % of peak away
from the best-fitting Gaussian. Two consequences:

- `CHAIN_SIGMA_AT_LEVEL_1` = 1.2, which `pyramid-plan.ts` inverts, **under-states level 1 by 24 %**.
  It says of itself that it is advisory and the body blur's residual pass absorbs it; a heavy tap
  has nothing to absorb it with, so this wave carries a measured table (`CHAIN_LEVEL_SIGMA`).
- Level 4's width by half maximum is **13.42 device px**, which is the 13.3 the ledger recorded.
  The reference's is 19.52. The gap is one third of an octave that the chain does not have.

---

## 2. The three candidates, and what each one's constant buys

All three are one constant, inert at the default, behind uniform slots added in `passes.ts`
(`heavyTap` and `heavyStep`, `d[108…115]`). `mapping.txt` is the full table; `predicted` there is
a simulation of what the renderer draws — the chosen level, reconstructed as the shader
reconstructs it, convolved with the discrete grid the shader integrates, reduced by half maximum,
which is the statistic reader A reduces its pair by.

### (i) A fractional pyramid level — `sizeHeavyLevelOffset`

Added to `scatterLod` inside the same clamp. **Dead upward at 1x, by the bit.** Against the inert
default, over the 18 ladder rows per profile: at offset +0.5 and +1.0, **18 / 18 1x captures are
byte-identical and 16 / 18 2x captures differ.** There is no level 5 on a 320 × 200 chain to
interpolate toward, so a positive offset lands on the level the gain already saturated to. It is a
real *narrowing* lever (offset −1.0 takes the 1x median from 14.36 to 7.61) and a real lever at
2x, where the chain is one level deeper and the gain has not saturated — but the wave needs
widening at 1x, which is exactly what it cannot do.

### (ii) A Gaussian at the tap — `sizeHeavyTapSigma` / `sizeHeavyTapSigma2x`, in device px

The CPU resolves the σ through the pyramid into a level, a residual σ in that level's texels and a
uv step (`heavyTapPlan`, on the measured `CHAIN_LEVEL_SIGMA`); the pass convolves a 9 × 9 grid of
that level at one-texel spacing, renormalised. The clamp is no longer a ceiling on the result,
because the residual carries the octave the chain lacks. **This is the only candidate that widens
at 1x**, and the mapping at 2x, where the reader can follow it:

| σ (device px) | level | residual (texels) | predicted | read (median) | ratio |
| --- | --- | --- | --- | --- | --- |
| 10 | 3 | 0.930 | 9.40 | 10.51 | 1.12 |
| 13 | 3 | 1.394 | 12.73 | 14.19 | 1.11 |
| 16 | 4 | 0.545 | 16.05 | 17.86 | 1.11 |
| 19 | 4 | 0.841 | 18.68 | 22.93 | 1.23 |
| 22 | 4 | 1.090 | 22.15 | 35.25 | 1.59 |
| 25 | 4 | 1.318 | 25.48 | 54.26 | 2.13 |

Monotone at 2x over the whole 10–25 range; **within 11–13 % of the prediction up to σ 16** and
outside 10 % above it. The prediction itself is exact arithmetic, so the drift above 16 is the
reader, not the tap — see §3.

**Cost, measured** (`e2e/bench/budget.spec.ts`, `apple / metal-3`, 60 interleaved rounds, the
mobile 390 × 844 @ 3 scene): the optics pass **1.416 → 2.528 ms**, the frame **2.684 → 4.356 ms**,
134 % → 218 % of the ~2 ms hypothesis, with the ordering control at 2.822 so the drift is smaller
than the effect. That is +1.1 ms for 80 extra reads of a 40 × 25-texel level. It is inherent to an
in-shader tap — a fragment pass cannot separate a 2D Gaussian — and it is **not** inherent to the
mechanism: see §5.

### (iii) A second chain level blended by a share — `sizeHeavySecondShare`

`mix(tap(scatterLod), tap(scatterLod + 1), share)`. **Dead at 1x, by the bit, for the same reason
as (i)**: 18 / 18 1x captures byte-identical at shares 0.25, 0.50 and 1.00, 16 / 18 2x captures
differing. Where `scatterLod` is already `chainMaxLod` the second tap *is* the first tap. At 2x it
moves the reader's median only 11.23 → 13.41 across the entire share range — one octave in
principle, a fifth of one in what reader A sees — and it can never reach past `chainMaxLod` either.

---

## 3. What the ladder could not read, and why it matters to G1

Clause 1 asks for reader A's heavy σ on the 1x impulse rows over 10–25 device px. **That ladder is
not readable with the instrument as it stands.** At 1x the reader's rows go 14.66 / 14.84 / 16.99 /
12.91 / 61.75 / 61.75 across σ 10 → 25 — non-monotone, and the last two are the reader parked on
its own bound (it parameterises the heavy component as `sharp + delta` with `delta ≤ 60·scale`).
At 2x the same constant reads monotonically over the same range.

The drawn kernel is **the same in device px at both scales at the same σ** — the same plan, the
same level, the same residual, because `bodySigmaCssFor` divides by the ratio and the raster's
texels per CSS px multiply it back. So the two columns disagreeing is the instrument: reader A's
window on `impulse` is half the dot pitch, 30 CSS px, which is 30 device px at 1x and 60 at 2x. A
heavy component of 19.5 device px does not fit in a 30 device px half-window; the reference's own
1x reading of 19.52 sits at that edge, and vitrea's per-row 1x spread at one true width of 13.42
(9.08 / 14.36 / 19.78, median 14.36 — the median is exact, the rows are not) is the same effect.

**G1 needs one of three things before it can fit the 1x width**: read the 1x width on the 2x rows
and carry it down by the halving claims §5.113 §2 established; or capture an impulse backdrop with
a wider dot pitch as a probe fixture; or fit against readers B / C, which is not the same quantity
(see §4). This is the single most consequential thing G0 found after the clamp.

**X5 held at every rung.** The worst thin-row (span ≤ 44) OKLab ΔE move against the inert default
is 0.00136, at σ 25 on `checkerboard-32__capsule-button`; every rung inside the range the wave
actually wants (σ ≤ 19) is at or under 0.00071. The sharp component is unmoved at 1x on every rung
of (i) and (iii) and moves under 5 % on (ii).

---

## 4. What the share law's lift does once the width is right

Rungs: the 0.14.0 material; W25's own declined rung (lift 0.45 at the old width); the width alone
at the reference's own 19.5 / 11.3 device px; and both. The objective is W25 G3's `share_check`
restated — `mean |log(web/native)|` over readers B and C on `checkerboard-32` / `-64` at spans
≥ 96, lower is better (`share-at-width.txt`).

| rung | 1x | 2x |
| --- | --- | --- |
| 0.14.0 | 0.2253 | 0.0964 |
| lift 0.45 at the old width | 0.3457 | 0.0964 |
| the width alone | 0.3438 | 0.2142 |
| both | 0.4340 | 0.2142 |

**It does not improve. It gets worse, and so does the width alone.** The lift's direction at 1x is
unchanged by the width: 0.2253 → 0.3457 at the old width, 0.3438 → 0.4340 at the new one. And the
right heavy width by itself takes the objective from 0.2253 to 0.3438 at 1x and 0.0964 to 0.2142 at
2x.

That is coherent rather than contradictory, and it says the objective was the wrong check.
Claims §5.113 §2 already measured that on these very rows vitrea is **32–46 % TOO WIDE at 1x on
every thick span, on both readers** (reference 1.14–1.30 device px against vitrea 1.66–1.90). A
single-Gaussian reader on a 32 or 64 CSS px pitch is dominated by the kernel's CORE, and vitrea's
core is already too wide; widening the heavy component or mixing more of it in widens the core
reading further. **The coarse checkerboards' single-width objective is a check on the SHARP
component, not on the heavy one, at any width.** W25 was right to decline the share on it and wrong
to expect the width to reverse it.

**The 2x lift is still inert with `sizeScatterFloor2x` = 1**: the two 2x columns are identical
between lift 0 and lift 0.45 because `kDeep` is already 1 at every span. But the **2x width is
fully reachable through candidate (ii) with that floor in place**, because the tap's width and
`kDeep`'s share are different mechanisms: at `sizeHeavyTapSigma2x` = 11.3 reader A reads 12.22 /
11.95 / 12.04 device px on `rrect-md` / `-ml` / `-lg` against the reference's 11.29 / 12.03 / 16.92
— within 8 % on `rrect-md` and within 0.7 % on `-ml`, with the floor untouched. That is clause 2's
2x half of the width met on two of three rows by one constant.

---

## 5. Verdict

**Candidate (ii), the Gaussian at the tap, is the mechanism.** It is the only one of the three that
widens the heavy component at dpr 1 at all — (i) and (iii) are inert to the bit there, and the
byte-identity table is the proof, not an argument. It moves the width monotonically over the whole
10–25 device px range in what the renderer draws, and where the instrument can follow it (2x) the
mapping from the constant to reader A's heavy σ is within 11–13 % up to σ 16 and outside 10 % above
it. At the reference's own 2x width it lands the 2x heavy component on the reference on two of
three rows.

**Two conditions on it, both for G1.**

1. **The cost has to come off, or be accepted at 218 % of the hypothesis.** The 9 × 9 in-shader
   grid costs +1.1 ms on the optics pass. The structural fix is the one the chain already uses for
   the body: a **third pyramid texture built by the existing separable blur** — two passes per
   source per frame, which measure 0.070 ms as `body-blur` on the same row — giving the same width
   exactly and continuously, at the cost of being one width per source rather than one per pixel.
   The reference's heavy width does not grade with the span at 1x (claims §5.113 §4), so the
   material can afford that trade; the 2x span grading `sizeScatterGainFar2x` carries would have to
   be re-expressed or retired. G0 did not build it because a spike's job was to find out which
   mechanism moves the width, and it now has.
2. **The instrument has to reach the 1x width** (§3), or the 1x constant is fitted on the 2x rows
   and the halving.

**The rows G1 should fit on, with the condition I expect:**

- **`sizeHeavyTapSigma2x` on `impulse__rrect-md` / `-ml` / `-lg` at 2x, reader A's heavy σ.**
  Well conditioned: the read moves 10.5 → 54.3 over σ 10 → 25, a lever of about 2.9 device px of
  reading per device px of constant near the reference's width, and 11.3 already lands two of the
  three rows. Expect a fit near 11–12.
- **`sizeHeavyTapSigma` (1x) on the same three rows at 1x — but only after §3's instrument
  question is answered.** As it stands the lever is non-monotone above σ 17 and the reader parks on
  its bound, so a 1x fit on these rows today would be fitting the instrument. If the answer is "carry
  it down from 2x", the prior is 19.5 device px (2 × 11.3 is 22.6, and the reference's own 1x
  reading is 19.52 — the halving is not exact on this row and the disagreement is itself a reading
  to record).
- **NOT the coarse checkerboards' single-width objective, for the width or for the share** (§4).
  It is a check on the sharp component. If G1 wants an off-row check for the heavy width, it needs
  one that separates the two components — reader A on a second impulse fixture, or reader C bounded
  to the interior rather than the whole region.
- **The share after the width, per scale**, with the expectation that the 1x share still cannot be
  raised on the checkerboards' objective and that the 2x share needs `sizeScatterFloor2x` to come
  off 1 or the lift applied before the floor — the width does not unblock either of those, and G0
  can now say that with the width right rather than as a conjecture.

## What this spike touched that is committed evidence

One thing: `resolvedMaterialSha256` in both profile documents, `9b7806cdefd1d1d6 →
4475b4dfa6155ce7` (light) and `eec7c2ea8dc89cae → 25a12c887e5b51cb` (dark), with a
`$comment-w26-g0` beside it saying why. The digest is over the fully resolved material, so adding
four constants at zero moves it even though no value and no pixel moved — the 33 goldens and the 36
reproduced captures are the proof of that, and `tuned-profiles.test.ts`'s own message asks for
exactly this re-recording. No profile VALUE moved; the canonical matrix, `web-captures/`,
`fixtures/` and `scenes.json` were never written.
