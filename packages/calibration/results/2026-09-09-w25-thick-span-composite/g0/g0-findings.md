# W25 G0 — the width instrument, the read on every thick cell, the size law's argument, the along-side reader

Findings, 2026-09-09. A spike: nothing here is a fit, a constant or a change. Every number was read
from fixtures already on disk — the reference fixtures under `apps/reference-apple/fixtures/`, the
two probe grids under `packages/calibration/results/`, and the canonical 0.13.0 web captures under
`packages/calibration/web-captures/` — all read-only. No native capture was taken; nothing under
`fixtures/`, `scenes.json`, `results/matrix.json` or `web-captures/` was written.

Files beside this one, each its own instrument with its header stating what it reads and in which
unit: `w25lib.py` (the three readers), `validate.py` / `validate.txt` (deliverable 1),
`widths.py` / `widths.txt` / `levels.txt` (2), `argument.py` / `argument.txt` (3),
`along-side.py` / `along-side.txt` (4), `grid-state.py` / `grid-state.txt` (5),
`identification.py` / `identification.txt` (6). `widths.json`, `along-side.json` and
`argument-probe.json` are the machine-readable rows behind them.

Units throughout: sigmas in **device px** unless a row says CSS px; levels in linear Rec.709 luma,
with differences also given in 8-bit display codes (the sRGB OETF applied to each side).

---

## 0. The headline, in six sentences

1. **The reference's kernel is not one Gaussian, and that is why every previous width number
   disagreed with every other.** Read on the same cell at 1x, the reference's width is **1.30**
   device px against a 16 CSS px checkerboard, **4.75** against a 32 px one and **6.25** against a
   64 px one (`argument.txt` Table 1). A single Gaussian gives the same answer at every pitch —
   validated to 0.00 % error on synthetics (`validate.txt`). So each of the ledger's width numbers
   is a true reading of a different part of the same two-component kernel.
2. **The thin surface and the thick surface differ in the heavy component's SHARE, not in a
   width.** At pitch 64 the thin cells still read 2.00–2.10 while the thick ones read 6.00–6.75;
   at pitch 16 all of them read 1.2–1.6. Reader A measures the share directly: **0.00 on the
   collapsed capsule and 0.47 (1x) / 0.69 (2x) on `impulse__rrect-md`** (`widths.txt` Table 1).
3. **Both components halve in device px between 1x and 2x; the single-width readers see the width
   grow because the share moves.** Reader A on the reference: sharp sigma **2.79 → 1.40** and heavy
   **19.52 → 11.29** on `impulse__rrect-md`, reproducing W24 G1's 2.87 / 1.40 and 28.9 / 11.1 to
   within 0.08 device px; the pair's single-width equivalent nevertheless goes **5.57 → 6.47**.
   The dossier's "vitrea's runs the other way" was comparing vitrea's single width with the
   reference's sharp component.
4. **The size law's argument is right and its knee is nearly right; what is missing is a residual
   above the knee.** Of six candidates, `sizeThickness(short side)` — the current law, knee 96 —
   scores best on both the width and the level in every group (r 0.95–0.998 against 0.68–0.96 for
   the short side, long side, area, sqrt(area) or radius, `argument.txt` Table 2). But the body
   level keeps moving above 96, by about a fifth of the thin-to-thick step per further span
   doubling, where `sizeThickness` is flat by construction.
5. **The along-side rim variation is a thickness term, not the lens**: it is present on a
   completely flat backdrop, absent at span 32 and 44, and saturates above 96 — and its shape is a
   corner-to-corner ramp along a straight side that vitrea's per-normal lit-edge factor cannot
   express at all.
6. **The collapse's key does not need a new capture to be read, and the answer is that it is not
   span.** The W21 probe grid is already seven attested runs at one sitting with per-cell byte-state
   frequencies recorded; `dark-solid__rrect-md` (96, uncollapsed) and `dark-solid__rrect-lg` (160,
   collapsed) are single-state in all seven. What a new capture would settle is `rrect-sm`, which is
   bistable — and whose majority state is byte-identical to the LIGHT grid's capture of the same
   scene.

---

## 1. Three width readers, validated (`validate.txt`)

The three readers live in `w25lib.py`. Each was generalised from the instrument the wave named, and
each generalisation is stated where it is made:

- **Reader A, the dot PSF** (`psf_fit`), from `results/2026-09-09-w24-lit-edge/g1/psf.py`. W24's
  numeric bounds (sharp sigma ≤ 4·scale, heavy ≥ 4·scale) are replaced by an *ordering*: both
  amplitudes non-negative and the heavy component parameterised as `sharp + delta, delta ≥ 0`. That
  keeps the bounds' purpose — the unbounded pair fits any profile as a large positive and a large
  negative Gaussian of the same width, which W24 recorded — while removing the ceiling this wave
  has to go past. The only ceiling left is the profile's own half-window, reported with every fit.
- **Reader B, the edge spread** (`edge_spread`), a Python restatement of
  `packages/calibration/src/metrics/material.ts:102` `blurEdgeSpread` and `:216`
  `singleEdgeRegion`, with `sigmaCeiling` (`material.ts:187–193`) made a parameter and one
  re-windowing pass added. The residual keeps the committed definition — the fit RMS as a fraction
  of the profile's own step height, which `packages/calibration/src/report.ts:391–397` glosses as
  "Large means σ is not identifiable."
- **Reader C, the whole-region sigma match** (`sigma_match`), from
  `results/2026-09-08-w22-resting-sweep/g0/read-stack.py:118–141`, with the grid raised from its
  **16.00** ceiling to 64 and two identifiability guards added (below).

**Validation** follows `results/2026-09-03-w13-ramp/g0/g0_validate.py`'s pattern — recover a known
kernel before reading the reference. Each backdrop raster is Gaussian-blurred at a true sigma of
1, 2, 4, 8, 16 device px, affinely compressed (gain 0.55, offset 0.02 linear) and quantised to 8
bits; the shape is `rrect-md`, body eroded 6 CSS px.

| reader | recovers within 5 % | where it stops, and why |
| --- | --- | --- |
| A (impulse) | sigma 2, 4, 8, 16 at both scales | sigma 1 misses by **8.2 %** at both scales. Not a bound: it is the instrument's floor — a 4 CSS px box sampled at 4 device px and quantised to 8 bits. |
| B (checkerboard) | sigma 1–2 at 1x, 2–4 at 2x | Saturates at about **one eighth of the backdrop's step pitch**. At 1x it reads 3.03 for a true 4 and 3.22 for a true 8; at 2x, 6.79 for 8 and 7.35 for 16. **Raising the ceiling does not help** — 8, 16, 32, 64 and 128 were all tried and the best row is usually the smallest ceiling. The binding constraint was never the ceiling; it is that a window bounded by the neighbouring step cannot hold a kernel wider than the step. |
| C (checkerboard) | sigma 1–4 at 1x, 1–8 at 2x | Saturates at about **a quarter of the pitch**. |
| C (impulse) | sigma 1–16 at both scales | Nothing inside the grid. |

**The two guards reader C needed, and what they caught.** The closed-form gain is
`cov(ref, target)/var(ref)`, so once the blurred reference is flat the denominator vanishes and the
affine rescaling fits the target's own quantisation dither at an arbitrary sigma. Measured on the
synthetic before the guards: a 16 CSS px checkerboard at 1x under a true sigma of 8 was matched at
**15.50 with a gain of 495**, and under a true sigma of 16 at **0.00 with a gain of 0** — two
confident numbers that mean nothing. The guards are (a) a material attenuates structure and does not
amplify it, so gains outside (0, 5] are refused, and (b) a region whose own standard deviation is
below one 8-bit code (3e-4 linear) has no structure to match a width against, and the answer is
"not identifiable", which is a reading. `photo__rrect-md` on the 1x reduced-transparency profile
returns exactly that.

**Answer to the wave's clause 1 on the two retired numbers.**

- *The sigma-match's 16.00 ceiling* is retired: with the grid at 64, the 2x dark nested base reads
  **20.00** with a residual of 0.80 of the region's own spread. That is not a reading either — it is
  past reader C's validated bound of 8 device px on a 16 CSS px checkerboard at 2x — but it is no
  longer a ceiling artefact, and the correct statement is now "≥ 8, and this backdrop cannot say
  more".
- *The edge-spread's unidentifiable residual* is **not** retired by raising the ceiling, and this
  wave should stop expecting it to be. The ceiling was never the binding constraint; the backdrop's
  step pitch is. On the canonical 16 CSS px checkerboard the reader identifies to 2 device px at 1x
  and 4 at 2x, and the reference's own thick width at 2x is above both.

---

## 2. The width and the level on every thick cell (`widths.txt`, `levels.txt`)

### 2a. Where the readers agree — the reading

`widths.txt` Table 3 marks a width a READING when two readers on the same image agree within 15 %
and both are inside their validated bounds. On the reference:

| cell | profile | B | C | verdict |
| --- | --- | --- | --- | --- |
| `checkerboard__rrect-md` | 1x light / 1x dark | 1.26 / 1.22 | 1.30 / 1.30 | READING, 3.5 % / 6.7 % apart |
| `checkerboard__rrect-ml` | 1x light | 1.21 | 1.20 | READING, 0.6 % |
| `checkerboard__rrect-lg` | 1x light | 1.14 | 1.30 | READING, 14.2 % |
| `checkerboard__toolbar-group` | 1x light | 1.34 | 1.50 | READING, 12.2 % |
| `checkerboard__rrect-sm` | 1x light | 1.30 | 1.30 | READING, 0.3 % |
| `impulse__capsule-button` (A+C) | 1x, both schemes | A 2.62 | C 2.60 | READING, 0.7 % |
| `impulse__capsule-button` (A+C) | 2x, both schemes | A 1.39 | C 1.50 | READING, 7.8 % |

Everything else disagrees, and every disagreement has one of two causes, both diagnosed:
one reader is past its bound (all the 2x checkerboard rows, `hc-text`, the nested base at 2x), or
the two readers are looking at different parts of a two-component kernel (§2c).

The A+C agreement on `impulse__capsule-button` is the strongest single result in this file: two
instruments of completely different construction — a parametric fit to a transmitted dot and a
non-parametric whole-region match — return **2.62 against 2.60** at 1x and **1.39 against 1.50** at
2x, and reader A's sharp component reproduces W24 G1's recorded 2.63 and 1.30
(`results/2026-09-09-w24-lit-edge/g1/g1-findings.md:157–164`) to within 0.09 device px.

### 2b. The headline widths, reference against vitrea

`widths.txt` Table 2, `checkerboard`, native | GPU | CSS, device px:

| cell | span | 1x native | 1x GPU | 1x GPU/nat | 2x native | 2x GPU | 2x GPU/nat |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-md` (light) | 96 | 1.26 B / 1.30 C | 1.66 / 1.80 | **1.32 / 1.38** | 6.18 / 6.75 † | 5.90 / 6.75 | 0.96 / 1.00 |
| `rrect-md` (dark) | 96 | 1.22 / 1.30 | 1.67 / 1.80 | **1.37 / 1.38** | 6.05 / 7.00 † | 5.89 / 6.75 | 0.97 / 0.96 |
| `rrect-ml` | 128 | 1.21 / 1.20 | 1.67 / 1.80 | **1.38 / 1.50** | 7.31 / 16.50 † | 5.92 / 6.50 | 0.81 / 0.39 |
| `rrect-lg` | 160 | 1.14 / 1.30 | 1.66 / 1.90 | **1.46 / 1.46** | 7.41 / 19.00 † | 5.50 / 6.50 | 0.74 / 0.34 |
| nested base (light) | 130 | 1.28 / 1.50 | 1.73 / 2.10 | **1.35 / 1.40** | 6.63 / 16.50 † | 5.48 / 7.25 | 0.83 / 0.44 |
| nested base (dark) | 130 | 1.23 / 1.50 | 1.67 / 2.10 | **1.35 / 1.40** | 6.52 / 20.00 † | 5.41 / 7.25 | 0.83 / 0.36 |
| `toolbar-group` | 44 | 1.34 / 1.50 | 1.70 / 1.90 | 1.27 / 1.27 | 2.17 / 3.10 | 3.45 / 4.25 | 1.59 / 1.37 |

† past the reader's validated bound at 2x (B: 4 device px; C: 8). Every 2x row on the canonical
16 CSS px checkerboard is a lower bound, on both sides.

Residuals: reader B's 0.0145–0.0344 of the step height on the reference (identifiable by
`report.ts:391–397`'s own reading) and 0.0070–0.0234 on vitrea; reader C's 0.30–0.83 of the
region's own spread — large, and large for a reason that is the wave's central finding (§2c).

**The one thing this table says without qualification: at 1x vitrea's kernel is 32–46 % too wide on
every thick span, in the same direction on both readers, on both schemes.** At 2x nothing on this
bed identifies the reference's width, so no comparable statement exists at 2x.

On `photo`, where both scales sit in a comparable regime, reader C reads native 6.50 → 11.25
(`rrect-md`), 7.25 → 12.25 (`rrect-ml`), 9.25 → 14.50 (`rrect-lg`) against vitrea 6.50 → 10.75,
6.25 → 10.50, 7.50 → 12.25 — **exact at 1x on `rrect-md` (6.50 against 6.50) and 14–19 % low on
the two largest spans**, with the gap widening as the span grows. That is the thick-span gap the wave was chartered
on, seen through the one backdrop that can carry it at both scales.

### 2c. Why the readers disagree, and what the disagreement is

The reference's width read on the same cell against three backdrop pitches (`argument.txt` Table 1,
reader C, 1x, both grids, all inside bound):

| pitch (CSS px) | `rrect-sm` 32 | `capsule` 44 | `rrect-md` 96 | `rrect-ml` 128 | `rrect-lg` 160 |
| --- | --- | --- | --- | --- | --- |
| 16 (`checkerboard`) | 1.30 | 1.60 | 1.30 | 1.20 | 1.30 |
| 32 (`checkerboard-32`) | 1.60 | 1.70 | 4.75 | 4.00 | 5.25 |
| 64 (`checkerboard-64`) | — ‡ | 2.10 | 6.25 | 6.75 | 6.00 |

‡ `rrect-sm` is 64 CSS px wide and centred, so on a 64 px checkerboard it lies inside one uniform
cell and has no step under it at all; its 8.50 is geometry, not material. The W9 light and W21 dark
grids agree with each other cell for cell in this table to within 0.75 device px everywhere except
that one geometrically invalid cell.

A single Gaussian returns the same sigma at every pitch — reader C recovers 1.00 / 2.00 / 4.00
exactly on the synthetic. The reference does not, so **the reference's kernel is not a single
Gaussian**, and every width in the ledger is a true reading of a different part of it. Reader A
measures the two components directly (`widths.txt` Table 1):

| cell | scale | sharp sigma | heavy sigma | heavy share | residual |
| --- | --- | --- | --- | --- | --- |
| native `impulse__capsule-button` (collapsed) | 1x | 2.62 | — | **0.00** | 0.055 |
| native `impulse__capsule-button` (collapsed) | 2x | 1.39 | 1.40 | **0.00** | 0.033 |
| native `impulse__rrect-md` | 1x | 2.79 | 19.52 | **0.47** | 0.049 |
| native `impulse__rrect-md` | 2x | 1.40 | 11.29 | **0.69** | 0.022 |
| landed GPU `impulse__rrect-md` | 1x | 1.67 | 9.08 | 0.23 | 0.035 |
| landed GPU `impulse__rrect-md` | 2x | 3.51 | 8.76 | 0.69 | 0.019 |
| landed CSS `impulse__rrect-md` | 1x | 1.46 | 12.68 | 0.73 | 0.043 |

Three readings follow, and they replace the dossier's framing of the same numbers:

- **The collapsed material transmits through ONE Gaussian.** Heavy share 0.00 at both scales on the
  collapsed capsule. W24 read its sharp sigma and recorded it as "the reference's kernel"; it is the
  collapsed reference's kernel, and the uncollapsed one has a second component carrying half its
  energy at 1x and two thirds at 2x.
- **Both components halve in device px from 1x to 2x** (sharp 2.79 → 1.40, heavy 19.52 → 11.29;
  the collapsed capsule 2.62 → 1.39). In CSS px both quarter. That is one consistent unit rule
  across the collapse state and across spans.
- **The single-width equivalent nevertheless grows** (5.57 → 6.47 on reader A; 1.30 → 6.75 on
  reader C over the checkerboard), because the heavy share moves from 0.47 to 0.69. So the ledger's
  "the reference's width halves and vitrea's doubles" compares vitrea's single width against the
  reference's sharp component. Read like for like, both grow: reference 1.30 → 6.75 and vitrea
  1.80 → 6.75 on `checkerboard__rrect-md`, native 2x/1x ratios 4.9–14.6 against vitrea's 3.2–3.8
  (`argument.txt` Table 4).

Vitrea's own pair moves the wrong way: its sharp sigma goes **1.67 → 3.51** where the reference's
goes 2.79 → 1.40, and it reaches the right heavy share at 2x (0.69, exactly the reference's) and
misses it at 1x (0.23 against 0.47).

### 2d. The levels (`levels.txt`)

Reference against the landed GPU tier, body over the declared shape eroded 6 CSS px, in 8-bit codes:

| cell | 1x light | 2x light | 1x dark | 2x dark |
| --- | --- | --- | --- | --- |
| `dark-solid__rrect-md` | +2.70 | +2.70 | **−3.07** | **−3.07** |
| `checkerboard__rrect-md` | +1.93 | +2.71 | +0.46 | +0.25 |
| `checkerboard__rrect-ml` | +0.37 | +1.28 | — | — |
| `checkerboard__rrect-lg` | −1.49 | −0.49 | — | — |
| `checkerboard__glass-over-glass` (base) | −0.97 | −0.04 | +0.20 | +0.04 |
| `photo__rrect-md` | −0.78 | −0.81 | **−5.41** | **−5.55** |
| `photo__rrect-ml` | −1.83 | −1.84 | — | — |
| `photo__rrect-lg` | −3.35 | −3.33 | −3.55 | −3.60 |
| `photo__glass-over-glass` (base) | −2.70 | −2.70 | — | — |
| `checkerboard__toolbar-group` | **+8.77** | **+9.34** | — | — |
| `photo__toolbar-group` | +5.81 | +3.40 | — | — |
| `impulse__rrect-md` | +5.93 | +5.98 | — | — |
| `hc-text__rrect-md` | +2.05 | +2.46 | — | — |
| `light-solid__rrect-md` / `-ml` | −0.30 / −0.09 | −0.30 / −0.08 | — | — |

The recorded miss reproduces: `dark-solid__rrect-md` reads **0.01527 native / 0.01298 GPU** against
claims §5.100 §7's 0.01527 / 0.01299 (`c9a-fidelity-claims.md:13747`); this reader calls it −3.07
codes where the ledger records −2.93, the difference being the body mask (this reader erodes
6 CSS px; the matrix's interior mask is its own).

Two levels are worse than the one the wave was chartered on and are not in the ledger's thick-body
entry: **`checkerboard__toolbar-group` at +8.77 / +9.34 codes** — the largest level miss among the
wave's thick cells, on a *calibration* row, and the toolbar's members are span 44 so the size law
treats them as thin — and **`photo__rrect-md` in the dark scheme at −5.41 / −5.55 codes**, nearly
twice the `dark-solid` miss the wave named.

The CSS tier's levels track the GPU tier's within 1.5 codes on every row except
`checkerboard__toolbar-group` (+9.11 / +11.13) and `checkerboard__rrect-md` at 2x (+3.74).

---

## 3. The size law's argument (`argument.txt`)

**Which quantity grades the reference.** Six candidates were scored against both the width and the
body level across the five spans of one grid and one backdrop (`argument.txt` Table 2). The answer
is the same in every group, in both grids, in both schemes:

| candidate | width r | level r |
| --- | --- | --- |
| **`sizeThickness(short side)` — the landed law, knee 96** | **0.95–0.97** | **0.988–0.998** |
| short side (raw) | 0.89–0.92 | 0.89–0.96 |
| sqrt(area) | 0.86–0.90 | 0.88–0.94 |
| long side | 0.82–0.86 | 0.83–0.90 |
| area | 0.81–0.85 | 0.79–0.88 |
| radius | 0.69–0.73 | 0.68–0.76 |

So **the size law's argument is the one the reference uses**: the short side, through a saturating
curve, at approximately the landed knee. Not the long side, not the area, not the radius. Clause 4's
question is answered in the current law's favour, and the wave does not need to re-key the argument.

**Is there a knee above 96?** `argument.txt` Table 3, W9 light grid, `checkerboard`:

| span | `sizeThickness` | width | body level | Δ level |
| --- | --- | --- | --- | --- |
| 32 | 0.0000 | 1.30 | 0.61484 | — |
| 44 | 0.0923 | 1.60 | 0.61299 | −0.00185 |
| 96 | 1.0000 | 1.30 | 0.67915 | **+0.06617** |
| 128 | 1.0000 | 1.20 | 0.69083 | **+0.01168** |
| 160 | 1.0000 | 1.30 | 0.70458 | **+0.01374** |

The same shape on `checkerboard-32` (+0.06123, +0.00673, +0.00914) and `checkerboard-64` (+0.02153,
+0.01613, +0.01755). **The width does not grade above 96 on any pitch** — at pitch 32 it reads 4.75 /
4.00 / 5.25 and at pitch 64 it reads 6.25 / 6.75 / 6.00 across spans 96 / 128 / 160, flat inside the
grid's own step. **The level does**, by about a fifth of the thin-to-thick step per further span
doubling, and it keeps going all the way to 160 where the landed curve has been flat since 96.

On the dark bed the same residual runs the other way over dark backdrops (`checkerboard` 0.04679 /
0.04636 / 0.04619; `photo` 0.04649 / … / 0.04490) and the same way over bright ones (`light-solid`
0.09598 / … / 0.10294; `hc-text` 0.05728 / … / 0.07861), so the above-96 term is a *level* term
whose sign follows the backdrop, not a monotone thickening.

**The unit.** Reference 2x/1x ratios, `argument.txt` Table 4 and reader A's components:

| quantity | reference 2x/1x | vitrea 2x/1x |
| --- | --- | --- |
| sharp sigma (reader A, `impulse__rrect-md`) | **0.50** (2.79 → 1.40) | 2.10 (1.67 → 3.51) |
| heavy sigma (reader A, same cell) | **0.58** (19.52 → 11.29) | 0.96 (9.08 → 8.76) |
| heavy share (same cell) | 0.47 → 0.69 | 0.23 → 0.69 |
| single-width equivalent, `photo__rrect-md` (reader C) | 1.73 | 1.65 |
| single-width equivalent, `photo__rrect-lg` (reader C) | 1.57 | 1.63 |

The reference's kernel is invariant in **neither** device nor CSS px — each component halves in
device px (quarters in CSS px) while the share moves the other way. A per-scale anchor is therefore
unavoidable, which the landed profile already has; what it does not have is a per-scale **share**,
and that is the quantity the reference moves.

---

## 4. The along-side reader (`along-side.txt`)

The reader keeps W24's quantity — the rim's peak excess over the body along the inward normal — and
indexes it by **position along the straight part of a side** instead of by the normal's direction.
The body is taken beside each point (depths 10–20 CSS px inward at that same position), so a lens or
a backdrop gradient under the surface is divided out of the level and left only in the rim. It
reproduces the recorded reading: 2x dark `dark-solid__rrect-md`, top edge min 0.0103 / max 0.0459
against claims §5.108 §1's 0.0442 → 0.0158 (`c9a-fidelity-claims.md:14204`), the difference being
the body reference and 16-bucket binning.

**Verdict: a thickness term, and not the lens.** Three findings, each on a FLAT backdrop where a
lens has no gradient to refract:

1. **It is absent on the thin controls and present on the thick ones.** `along-side.txt` Table 2,
   native, corner-to-corner range in linear luma:

   | backdrop / profile | 32 | 44 | 96 | 128 | 160 |
   | --- | --- | --- | --- | --- | --- |
   | `light-solid` 1x light | 0.0000 | 0.0000 | 0.0187 | 0.0197 | 0.0145 |
   | `dark-solid` 1x dark | (0.0132) ¶ | 0.0016 | 0.0226 | — | 0.0180 |
   | `mid-dark-solid` 1x dark | 0.0259 | 0.0061 | 0.0345 | — | 0.0317 |

   ¶ the W21 grid's `dark-solid__rrect-sm` is the compromised cell of §5 and is quoted, not used.

2. **It saturates at the same knee the level does.** Range and range/mean rise between span 44 and
   96 and then stop: `light-solid` 0.0000 → 0.0187 → 0.0197 → 0.0145; `dark-solid` 0.0016 → 0.0226 →
   0.0180. So it rides `sizeThickness`, exactly like the terms already on that curve.

3. **It cannot be the lens.** `dark-solid` and `light-solid` are uniform, so there is no backdrop
   gradient to refract, and the grading is at its clearest there. On `checkerboard` the same reader
   correlates 0.85–0.96 with the backdrop's own level under the body (`along-side.txt` Table 3) —
   that IS the lens, and it is a different, much larger signal that swamps the thickness term. The
   two are separable only on the solids.

**What its shape is, and why vitrea cannot express it.** On every thick cell at 1x the four sides'
slopes are exactly antisymmetric — `dark-solid__rrect-md` 1x dark reads top −0.000192, bottom
+0.000192, left −0.000379, right +0.000379 luma per CSS px — so the rim is bright at the top-left
and bottom-right corners and dim at the other two: a smooth diagonal field over the surface, not a
function of the normal. Slope × straight-side length reproduces the range on the thick shapes
(0.000192 × 120 = 0.023 against a range of 0.0232), so it is a corner-to-corner ramp, not a
mid-side dip. vitrea's lit-edge factor `pow(|dot(n, axis)|·√2, p)` is exactly 1 everywhere on a
straight side, and the landed GPU captures confirm it: range **0.0015–0.0083** on the same cell
against the reference's 0.0206–0.0357 (`along-side.txt` Table 4).

**One thing this reader found that was not being looked for.** At 2x the four sides stop being
equal: 2x dark `dark-solid__rrect-md` reads mean 0.0330 (top) and 0.0313 (left) against 0.0168
(bottom) and 0.0176 (right), where every side at 1x reads 0.0248–0.0251. The 2x reference carries a
top-left/bottom-right asymmetry in the rim's *mean*, not only in its gradient, and the 1x reference
does not. Recorded, not explained.

**Consequence for the wave.** Under the Design's own test — "if it is a thickness term (graded with
span, flat on the capsule), it is this wave's" — the term is this wave's. But it is a *position*
term on a straight side, and vitrea's rim law has no position argument at all, so taking it means
giving the lit-edge factor a coordinate along the side, not adjusting a constant.

---

## 5. The dark grid's state flip (`grid-state.txt`)

**The grid already records its own bistability, and 18 of its 56 cells have it.** The W21 probe
grid's `manifest.json` was materialised by the majority byte-state per cell across **seven attested
runs at one sitting** (`probe/provenance.json`: "majority byte-state per cell across the attested
runs (frequency-settled, claims §5.30); shares recorded per cell"), and it records `observedStates`
and each state's share. Eighteen cells observed two states, most at a 6:1 share
(`grid-state.txt` Table 4).

**The tracker's contradiction, resolved into two halves.** `tech-debt-tracker.md:874–882` records
that the dark grid collapses `dark-solid__rrect-sm` (32) and `dark-solid__rrect-lg` (160) and not
`dark-solid__rrect-md` (96). All three levels reproduce exactly — 0.011007 / 0.015265 / 0.011007
against the backdrop's own 0.011711 (`grid-state.txt` Table 5, tracker's 0.0110 / 0.0153 / 0.0110):

- **`rrect-sm` is the state flip, and it is demonstrable.** It is one of the eighteen bistable cells
  (2 states, 6:1). Its majority state is **byte-identical** (SHA-1 over the PNG) to the W9 LIGHT
  grid's capture of the same scene — and so is `light-solid__rrect-sm`, the other bistable
  `rrect-sm`-over-a-solid cell. For `dark-solid` that identity is ambiguous, because a fully
  collapsed surface has stopped following the scheme and *would* look the same in both. For
  `light-solid` it is not ambiguous at all: the file reads a body of **0.96659** over a backdrop of
  0.8918 — a bright, light-scheme appearance — while the dark grid's `light-solid__rrect-md` and
  `-lg` read 0.09598 and 0.10294, and `light-solid`'s luminance is far above the tone response's
  0.14 upper edge so nothing over it collapses in either scheme. The dark grid's `rrect-sm`-over-a-
  solid row is therefore not a dark-scheme reading, and the same flip lands on its `dark-solid`
  sibling. (These two files are the only cross-directory duplicates among the 239 fixture
  PNGs of the six canonical profiles and the two grids that are not a grid deliberately reusing a
  canonical cell; the full scan is in `grid-state.txt` Table 1.)
- **`rrect-md` against `rrect-lg` is NOT a state flip, and it survives.** Neither cell is in the
  bistable eighteen: both were single-state in all seven attested runs at one sitting. So the
  reference really does collapse a 160 px surface over `dark-solid` and not a 96 px one, and a size
  law that collapses the large and not the middle is still not a size law.

**What a native re-capture would settle, and what it would not.** It would *not* settle the
`rrect-md`/`rrect-lg` contradiction: that capture has already been made, seven times, at one
sitting, and it is stable. What is worth the console session is narrower and different:

1. **`dark-solid__rrect-sm` and `light-solid__rrect-sm` re-captured under the dark scheme**, to
   replace two fixtures that are the light grid's files.
2. **`dark-solid__rrect-ml` (128) and intermediate spans (48, 64, 80)**, which have never been
   captured over `dark-solid` in either scheme. Three points cannot show where a collapse turns on
   and off; five or six can.
3. **The confound the canvas creates.** On the 320×200 canvas the short-axis clearance falls with
   span: 84 CSS px at 32, 52 at 96, **20 at 160**. `rrect-lg`'s margin is a quarter of `rrect-md`'s,
   so "the collapse keys on span" and "the collapse keys on how close the surface is to the window's
   edge" fit these fixtures equally well and nothing on disk separates them. Capturing `rrect-lg` on
   a larger canvas, or `rrect-md` pushed to a 20 px margin, would — and that is a scene change, not
   just a capture.

Note also that in the dark scheme the whole contrast is small: the "uncollapsed" `rrect-md` sits
0.00355 linear above the backdrop against the light scheme's 0.46803, so the dark grid's
contradiction is a **6-code** difference between collapsed and not, where the light grid's is 100.

---

## 6. The identification table (`identification.txt`)

For each constant a thick-span law would carry, which rows separate it. Entries are stated rules,
each derived from something citable: the width levers from `validate.txt`'s identification bounds
and the reference's own measured width at that cell; the knee lever is the landed law
(`material.ts:3140–3188`) differentiated with respect to `sizeSpanMax`; the collapse lever is the
tone response evaluated at the row's own backdrop and span (`scenes.json:50–68`). The `kn` column is
a derivative in share-per-CSS-px and the width columns are indicators, so the condition numbers
inherit that choice of scale; every verdict below is read off which entries are **zero**, which does
not.

| constant | (i) current bed | (ii) + `rrect-lg` and the stack into calibration | (iii) + the grids as captured (1x only) | (iii+) the grids at both scales | (iv) the grids whole, both scales |
| --- | --- | --- | --- | --- | --- |
| sharp sigma 1x | 7 rows, spans 32–128 | 10 rows, spans 32–160 | **63 rows, spans 32–160** | 63 | 63 |
| sharp sigma 2x | 6 rows, **spans 32–96 only** | 7 rows, **spans 32–96 only** | 6 rows, **spans 32–96 only** | **52 rows, spans 32–160** | 52 |
| heavy share | 4 rows, spans 44 & 96 | 4 rows, spans 44 & 96 | **24 rows, spans 32–160** | 44 | 44 |
| knee / argument | 17 rows, lever 0.002 | 25 rows, lever 0.002 | 61 rows, lever 0.002 | 73 | 79 |
| body level | 34 rows | 48 rows | 118 rows | 202 | 238 |
| collapsed body level | 8 rows, spans 44 & 96 | 10 rows, spans 44 & 96 | 8 rows, spans 44 & 96 | 8 | **24 rows, spans 32–160** |

**Five things this decides.**

1. **The 2x width above span 96 is identified by nothing, on either bed shape (i) or (ii).** Every
   2x row that identifies a width is span 32, 44 or 96; `checkerboard__rrect-ml` and `-lg` at 2x
   read 16.50 and 19.00, past reader C's bound, and reader B saturates at 7.3 there. Moving
   `rrect-lg` and the stack out of holdout adds **one** 2x width row and it is at span 96. So
   **shape (ii) does not buy the constant the wave most needs.**
2. **The probe grids as they stand on disk do not buy it either**, because both grids are 1x. Shape
   (iii) takes the 1x width from 7 rows to 63 and the heavy share from 4 to 24, and leaves the 2x
   width at 6 rows, spans 32–96. The amendment that answers the wave is **(iii+): the grids captured
   at both scales.**
3. **The heavy share is the constant the current bed is thinnest on, and the one that matters
   most.** §2c shows it is what separates the thick surface from the thin one and what moves between
   scales. Today four rows carry it, all `impulse` or `checkerboard-64`, at two spans — and the
   `impulse` rows measure the *collapsed* material (§2c), whose share is 0.00. Effectively the
   uncollapsed heavy share is carried by nothing on the canonical bed. The coarse checkerboards are
   the only fixtures that carry it.
4. **The collapsed body's level needs the grids' SOLID backdrops, which a "structured harness set"
   would exclude.** Shape (iv) is the only one that takes it past two spans.
5. **The knee is weak everywhere and no bed shape fixes it.** Its lever is exactly 0 at span 96 (a
   smoothstep's derivative vanishes at its own edge) and 0.002 above it, entirely through the `far`
   decline — the anchor `material.ts:847–858` exists because the knee saturates. No thick span
   carries more than 0.002 in any of the five shapes. This is not an argument for moving the knee:
   §3 shows the knee is approximately right and that what is missing above it is a *level* residual,
   which the level column identifies at 118–238 rows.

**The recommendation this supports** (the ruling is Decision Log 2's, with the user): the parent's
preference for shape (iii) over shape (ii) is confirmed and should be sharpened to **(iii+)/(iv)** —
the probe grids declared as a harness set **captured at both scales, with their solid backdrops
kept**. Shape (ii) costs the two largest spans as the independent check and returns one 2x row at a
span the bed already has. Shape (iii) as the grids stand returns nothing at 2x.

---

## 7. What this changes for the wave, and what should be recorded either way

**Corrections to the wave's own premises.**

- The Design's "the reference's width halves in device px from 1x to 2x and quarters in CSS px;
  vitrea's doubles" is true of the reference's **sharp component** and of vitrea's **single width**.
  Read like for like both grow. The quantity that moves between scales is the heavy **share**
  (0.47 → 0.69), which vitrea reaches at 2x and misses at 1x (0.23).
- Clause 1's "the edge-spread's 'not identifiable' residual retired as a reading" is not achievable
  by raising the ceiling: the backdrop's step pitch is the binding constraint. On the canonical
  checkerboard the edge spread identifies to 2 device px at 1x and 4 at 2x, full stop.
- Clause 4's question is answered without changing anything: the argument is the short side through
  a saturating curve at about the landed knee.

**Gaps to macOS this read found that are not in the ledger** (each belongs in a claims section, a
Deferred list or `specs/tech-debt-tracker.md`, with the rows that would close it):

1. **The two-component kernel's share is the thick-span mechanism**, and vitrea's law has no share
   at 1x that matches (0.23 against 0.47).
2. **At 1x vitrea's kernel is 32–46 % too wide on every thick span**, consistently on two readers,
   both schemes.
3. **On `photo`, vitrea's width falls 14–19 % short on `rrect-ml` and `rrect-lg`** and matches on
   `rrect-md` — a gap that opens with span.
4. **The body level keeps grading above span 96** and the landed `sizeThickness` is flat there.
5. **`checkerboard__toolbar-group` is +8.77 / +9.34 codes**, the largest level miss among the wave's
   thick cells, on a calibration row, and it is not in the ledger's thick-body entry.
6. **`photo__rrect-md` in the dark scheme is −5.41 / −5.55 codes**, nearly twice the `dark-solid`
   miss the wave was chartered on.
7. **The along-side rim term is a position term on a straight side** that vitrea's per-normal
   lit-edge factor cannot express; the reference's field is a diagonal corner-to-corner ramp.
8. **The 2x reference's rim mean is top-left/bottom-right asymmetric** where the 1x reference's is
   symmetric.
9. **Two W21 dark-grid fixtures are the W9 light grid's files** (`dark-solid__rrect-sm__rest`,
   `light-solid__rrect-sm__rest`), both flagged bistable in the grid's own manifest. Whatever the
   bed amendment decides, these two should be re-captured or withdrawn.
10. **Span and canvas clearance are confounded on the 320×200 canvas** (84 / 52 / 20 CSS px at spans
    32 / 96 / 160), so no fixture on disk separates a size-keyed collapse from an edge-proximity one.

**What no bed on disk can answer, so that the wave does not spend effort trying.** The reference's
kernel width at 2x on a thick uncollapsed surface. The canonical checkerboard saturates both readers
below it; `photo` gives a single-width equivalent but cannot separate the two components; the
`impulse` rows are collapsed. It needs a coarse structured backdrop at 2x, which exists in neither
grid and in no profile.
