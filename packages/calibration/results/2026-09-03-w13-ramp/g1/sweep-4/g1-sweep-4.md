# W13 G1, fourth round — the far start fitted on the W14 bed, the 2x null re-verified (2026-09-03)

The third round reached the 1x band on every calibration cell and failed one holdout row for
the form's own arithmetic: `sizeThickness` saturates at `sizeSpanMax` 96, so spans 96 to 160
all started at the thick anchor while the reference's start falls 0.512 → 0.501 → 0.410
across them, and `rrect-lg` overshot its interior by 33% (`../sweep-3/g1-sweep-3.md` §5.2;
claims §5.67 §4). This round sweeps the fourth form W13 Decision Log 6 declared — the start
declining past the thickness knee along the scatter facet's own curve to a new far anchor —
and it is the first round taken on the **W14 bed**: main at `8eebae4`, the outer shadow's
two-term composite landed, the three 2x texture-tier floors gone (claims §5.66 §6). Under
X8 the second wave to land re-runs its dry run on the first's bed, so every comparison here
is against that bed, not the W12 close.

## 1. The form, and the prediction written before the first capture

    kDeep(span) = floor + (1 − floor) · smoothstep(sizeSpanMin, sizeScatterSpanMax, span)
    s₀(span)    = thin + (thick − thin) · sizeThickness(span)
                + (far − thick) · smoothstep(sizeSpanMax, sizeScatterSpanMax, span)      [NEW]
    s(u, span)  = (1 − kDeep) + max(0, s₀ − (1 − kDeep)) · max(0, 1 − u / U)

One constant per scale, `sizeScatterRampStartFar1x` / `…2x`; both curves are the material's
own. `paper4.py` (no GPU) projected the form on the real spans before the first capture, and
it says two things the grid then measured: the far anchor touches only `rrect-ml`,
`glass-over-glass` and `rrect-lg` (the thin cells and `rrect-md` sit on the curve's foot and
are bit-identical at every far value), and matching G0's own `rrect-lg` start of 0.410 needs
far ≈ 0.21 — below the declared grid's floor of 0.30, which is why the refinement went down.

## 2. The 1x grid, then the refinement (`1x-far.tables.txt`, `1x-far-refine.tables.txt`)

Thin 0.72 / thick 0.52 / reach 80 held at the third round's fitted optimum; far over
{0.30, 0.35, 0.40, 0.45, 0.52} and then {0.15, 0.20, 0.25}. The last value, 0.52, is the
third form itself (far = thick), so the grid contains its own baseline.

**S1 and S4 pass at every one of the eight points.** No calibration or validation row falls
(worst Δ`ssimMean` +0.0000), and `ssimBand` rises on every checkerboard cell: `rrect-sm`
+0.0048, `capsule-button` +0.0059, `rrect-md` +0.0023, `toolbar-group` +0.0019 at every point
— the far anchor does not reach them — and `rrect-ml` from +0.0042 (far 0.52, the third form)
to +0.0060 (far 0.15). The only cell that moves is `rrect-ml`, and it moves the way the paper
predicted: as far falls its interior closes toward the reference (`interiorStdDev` 0.0962 at
0.52 → 0.0934 at 0.30 → 0.0912 at 0.15 against a native 0.0865, the gap from 0.0097 to
0.0047) and its band rises. Its `ssimInterior` moves 0.9770 → 0.9782 the same way.

| far | `rrect-ml` band Δ | `rrect-ml` `isdW` (native 0.0865) | interior objective |
| --- | --- | --- | --- |
| 0.52 (third form) | +0.0042 | 0.0962 | 0.05027 |
| 0.45 | +0.0051 | 0.0952 | 0.05016 |
| 0.40 | +0.0052 | 0.0946 | 0.05015 |
| 0.35 | +0.0053 | 0.0941 | 0.05017 |
| 0.30 | +0.0051 | 0.0934 | 0.05013 |
| 0.25 | +0.0052 | 0.0927 | 0.05006 |
| 0.20 | +0.0056 | 0.0921 | 0.05002 |
| 0.15 | +0.0060 | 0.0912 | 0.04989 |

`ssimOutside` moves by at most −0.0006 (`toolbar-group` 0.9278 → 0.9272; `rrect-ml`
−0.0005; the capsule −0.0002) at every point, the same size at far 0.52 as at 0.15 — the
third form's coverage-ramp reading (claims §5.67 §5), not this constant's.

## 3. The choice: far 0.20

The band is flat within the bed's noise below far 0.30 (the second round measured 0.0004 of
band over a factor of two in reach; here 0.0004 separates 0.30 from 0.15) while the interior
keeps closing and the objective keeps falling, so the calibration cells alone would take the
grid's floor and keep going. The cell this form exists for is holdout and cannot vote. So
the tie inside the noise is broken by the reference's own reading: G0's `rrect-lg` start of
0.410 re-expressed through the form is far = 0.207, and **far 0.20** puts `rrect-lg`'s start
at 0.407 and its excursion at 0.171 against G0's implied 0.174 (`paper4-chosen.txt`) — a
measured grid point, inside the swept range, within noise of the band's best, and the number
the reference itself gives. Not a paper prediction landing on a constant: the point was
captured, and the reading says it cannot be told from its neighbours on the calibration
cells.

## 4. The 2x null, re-verified bit-exact on this bed (`2x-null.identity.txt`)

Four points on the 2x light profile — thin2x {0.46, 0} × far2x {0.15, 0} at thick 0.17,
reach 100 — render **identically: maximum |difference| 0 over 20 cells × 774 measurements**
on every pair. The far anchor changes nothing at 2x, as the form says it must (far2x 0.15
sits below thick2x 0.17, and every 2x start already sat below its cell's deep value), and
neither does the thin one. The null the third round verified against the pre-ramp branch
holds under the fourth form and on the W14 bed.

**The widths pedestal, now against the W14 bed.** At 2x the branch differs from `main` before
any ramp acts, because it carries candidate A's device-pixel widths (§5.64 §3): on this bed
that reads `ssimMean` `rrect-sm` +0.0008, `capsule-button` +0.0019, `rrect-md` −0.0061,
`rrect-ml` −0.0161, `toolbar-group` +0.0001, and `ssimBand` +0.0248 / +0.0245 / −0.0152 /
−0.0194 / +0.0044. Every 2x number in the confirmation below is that pedestal and nothing
from the ramp.

## 5. The confirmation, read once (`confirm.tables.txt`, `matrix-confirm.json`)

At thin 0.72 / thick 0.52 / **far 0.20** / reach 80 at 1x and thin 0.46 / thick 0.17 / far
0.15 / reach 100 at 2x; four profiles, calibration + validation + holdout, holdout read for
the first time under this form; every row against the W14 bed. GPU custody 23:26:05–23:28:07.

### 5.1 The stops, with numbers

**S1 — no 1x row below its W14-bed value by more than 0.002. MET, on every row including
holdout.** The largest 1x `ssimMean` fall anywhere is `hc-text__capsule-button` −0.0003; the
next `hc-text__rrect-md` and `impulse__rrect-md` at −0.0001. `checkerboard__rrect-lg`, the
row the third form failed at −0.0026, reads **+0.0056**.

**S4 at 1x — `ssimBand` rises on every checkerboard cell, `ssimInterior` beside it. MET.**

| cell | set | `ssimBand` | Δ | `ssimMean` Δ | `interiorStdDev` web / native | gap |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-sm` | calibration | 0.9723 | +0.0048 | +0.0002 | 0.1619 / 0.1549 | 0.0070 |
| `capsule-button` | calibration | 0.8872 | +0.0059 | +0.0005 | 0.1385 / 0.1424 | 0.0039 |
| `rrect-md` | calibration | 0.9340 | +0.0023 | +0.0003 | 0.1051 / 0.1131 | 0.0080 |
| `rrect-ml` | calibration | 0.9429 | +0.0056 | +0.0008 | 0.0921 / 0.0865 | 0.0056 |
| `toolbar-group` | calibration | 0.7244 | +0.0019 | +0.0000 | 0.1424 / 0.1481 | 0.0057 |
| `glass-over-glass` | holdout | 0.9499 | +0.0058 | +0.0016 | 0.1321 / 0.1321 | **0.0000** |
| `rrect-lg` | holdout | 0.9537 | **+0.0136** | **+0.0056** | 0.0731 / 0.0650 | 0.0081 (12% over) |

`rrect-lg` is the row this form exists for: the third form read its interior at 0.0865
(33% over the reference) and the W12 close at 0.0540 (17% under); the fourth reads 0.0731,
12% over, with the largest band rise on the bed. `glass-over-glass` keeps the third form's
exact interior agreement.

**S4 at 2x, as the null — MET** (§4): the ramp changes no pixel at 2x.

**S2 at 2x, re-read on the W14 bed — MET.** The three rows W12 floored and W14 met: `rrect-ml`
**0.9585**, `glass-over-glass` **0.9664**, `rrect-lg` **0.9509**, every one above 0.93 — and
every one **below the W14 bed** by the widths pedestal: −0.0161, −0.0098, −0.0171. The ramp
contributes exactly nothing to those numbers (§4); candidate A's device-pixel widths do, and
they were carried into this wave by decision (W12 Decision Log 7). The declaration has to say
that landing this branch lowers three 2x rows the W14 landing raised, by 0.010–0.017, while
they stay 0.02–0.04 above the bound whose floors came off.

**S3 at 2x — `interiorStdDev` within 0.005 of native.** Three of five calibration cells, as
before: `rrect-sm` 0.0011, `rrect-md` 0.0012, `rrect-ml` 0.0010 pass; `capsule-button` 0.0052
(by 0.0002) and `toolbar-group` 0.0071 miss. Holdout: `rrect-lg` 0.0023 pass, `glass-over-glass`
0.0047 pass. Unchanged from §5.64 §3, as the null requires.

**S5 — the solids, `photo` and the tinted cells by ≤ 0.001 in any adopted metric; `ssimOutside`
by ≤ 0.001 on every cell. MET on the first clause; the second misses on one 1x holdout row by
0.00005.** Every solid and `impulse` row reads +0.0000 on band, mean and outside at both scales;
`photo` and the tinted cells move by ≤ 0.0003. `ssimOutside` at 1x: `hc-text__capsule-button`
(holdout) **−0.00105**, the third form's −0.00112 shifted by a twentieth of the tolerance;
`toolbar-group` −0.0007, `rrect-ml` −0.0005, `hc-text__rrect-md` −0.0005, `rrect-lg` −0.0004.
The 2x departures (up to −0.0029 on `hc-text__capsule-button`) are the widths pedestal, which
the null proves. The 1x miss is the coverage-ramp reading claims §5.67 §5 recorded: a body law
touching the outside of the contour by about a thousandth on one high-contrast-text cell. Not
this constant's — it is the same size at far 0.52 as at 0.15 (§2).

### 5.2 The dark scheme

Every dark row rises or holds. 1x: `capsule-button` band +0.0191, `rrect-md` +0.0059,
`glass-over-glass` (holdout) +0.0146 with `ssimMean` +0.0046; `photo` rows ±0.0002. 2x: the
widths pedestal again (`capsule-button` +0.0298, `rrect-md` +0.0154 / +0.0034,
`glass-over-glass` +0.0100 / +0.0029), since the ramp is inert there.

## 6. What this asks of the declaration

1. **The 1x half of the wave is reached, holdout included.** S1 met on every row, S4 met on
   every checkerboard cell with the largest rise on the holdout cell the form was built for,
   `rrect-lg`'s interior from 33% over to 12% over, `glass-over-glass`'s exact. Eight
   constants; the 1x four fitted in the renderer (thin 0.72, thick 0.52, far 0.20, reach 80),
   the 2x four provisional by necessity.
2. **The far anchor was chosen by the reference's reading inside the calibration cells'
   noise**, not by the grid's floor: the band is flat within 0.0004 below far 0.30 and the
   interior keeps closing, so a calibration-only pick would run to the edge and past G0's own
   `rrect-lg` start. 0.20 is the measured point that carries that start (0.407 against 0.410).
   A declaration that wanted the runtime's preference alone would go lower and should say why.
3. **The 2x null is a property of the law under this form too** — four points identical over
   774 measurements a cell — and the 2x constants remain unfittable here. The 2x gap stays in
   the deep value (W13 Deferred).
4. **Landing this branch lowers three 2x rows the W14 landing raised**, by 0.010–0.017, to
   0.9585 / 0.9664 / 0.9509 — above 0.93, S2 met, floors gone — and it is the widths, not the
   ramp. That trade was made when the widths were carried into this wave; the declaration
   states it as a number the bed will show.
5. **One `ssimOutside` row misses S5 by 0.00005**, the third form's coverage-ramp gap unchanged.
   A body law should be a null outside the contour; something at the coverage ramp is not, on
   one high-contrast-text cell, by a thousandth.
6. **The five review findings are on the branch** (`7de3d76`): the group proxy's σ as the
   maximum projected σ over members (`groupScatterSigma`), the CSS tier's zero-mix fast path
   under the device-pixel division, both media feeds on the supplied window, the proxy e2e
   helper and every spec on their fixtures' extents, the demo readout over the plate's own
   box. The platform-web e2e suite passes on Chromium (126) and the demo's (34).
