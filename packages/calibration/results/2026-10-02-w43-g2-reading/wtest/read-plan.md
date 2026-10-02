# The w-test and the ladder: what is computed, from which frames, before either is read (W43 G2 stage two, 2026-10-02)

Charter clauses 8 and 9, G2 "After G1b", X46 and X47; claims §5.200b. This file and `wtest_read.py` are
committed **before** the w-test's read runs, in a commit of their own. At that commit no G1b probe or
ladder frame has been decoded by this child. `check.txt` is the check mode's output: it hashed and counted
the frames but decoded only 0.5 pixels.

## 1. The w-test (clause 8): read once

**What is computed.** Exactly the declaration in force, `4f90f910…` (the chain's last line in
`results/2026-10-01-w43-g0-declaration/declaration.sha256`), item `wTestStatistic` with its prediction
item `wTestPrediction`, through the declaration's own code imported unchanged. `wtest_read.py` refuses to
run unless each of these hashes as the declaration pins it: `wtest.py`, `rehearse.py`, `w42frames.py`,
`support.json`, `prediction.json`, `probe-bed.json` and `scenes-w43-probe.json`.
- **Regions:** `support.json`'s supported free-side regions, the `median` statistic under the `declared`
  support (k in [1.4, 2.5]). They are regenerated from the declared rule and refused unless they hash as
  recorded (`rehearse.load_support`). The counts are 4, 2, 3 and 2 in light active, light receded, dark
  active and dark receded.
- **Per region and channel:** M_x = T_x⁻¹(y_x), with y the region median of the plurality frame, and
  r = (M₀.₂₅ − C) / (M₀.₅ − C), averaged over channels (`wtest.invert`, `wtest.ratio`). The per-channel
  ratios are printed beside it. The resolution is dr as declared (`wtest.ratio`).
- **T_x:** native, per channel and stratum, through the probe's own greys at x
  (`rehearse.grey_tables`):
  - at 0.25, G1b's seven grey levels on the capsule (t = 0) and rrect-md (s = 96);
  - at 0.5, W42's;
  - in dark at s ≥ 96, only ordinates ≤ 208.
- **Verdict per endpoint:** `wtest.verdict`. PASS iff |r − 0.5| ≤ dr on every supported, measured region,
  at least one. FAIL otherwise, with the measured r. A region whose 0.25 median is censored (≥ 250 or ≤ 5)
  is UNMEASURED. The prediction is r_pred = 0.5 in all four endpoints (`prediction.json`).
- **The lifted side,** read and reported, never gated: r_lift on `support.json`'s lifted regions. Beside
  it, `wtest.lifted_reading` gives the implied λ₀.₂₅ and the declared ramp's two scalings of W42's
  fitted λ₀.₅.

**From which frames.**
- **0.25:** for each of the 29 probe cells per 2x endpoint, the plurality frame of G1b's three normal runs
  in the `probe-0.25-2x-{active,receded}` passes, read from the owner-controlled copy of
  `w43-archive-g1b`. That is asset `e17f7efa…`, tree verified entry by entry against inventory
  `9c7fbd86…`, each frame's SHA-256 its name. G1b's raw root, stop evidence, pre-launch, restore and
  release directories are denied for the process. The check found every one of the 116 cells
  unanimous over its three runs.
- **0.5:** the plurality of W42's seven normal runs per counterpart, read from `w42-archive` (asset
  `1e3d6e65…`, inventory `5481795e…`) through W42's guarded Reader. Only the calibration and validation
  roles are opened, H is never requested, and `~/vitrea-w42/g1` is denied (`w42frames.extract`). Every
  re-extracted frame must be the frame G0's rehearsal 3 read, by SHA-256. One of the 116 has two states,
  and its plurality is read, as at G0.

**Once.** `wtest_read.py read` refuses if `reading.json` exists. Its output (`reading.json`,
`reading.txt`) is committed as it ran. Neither the support, the statistic, the resolution nor the rule
moves after it, and the ladder below cannot amend it (X47).

## 2. The ladder (clause 9): described, after the w-test

These are the declared readings (item `ladderReadings`), descriptive, with no fit and no gate. They are
read after the w-test's read is committed. They use the same functions and the same frames as the
w-test, plus G1b's ladder passes at x = 1, 0 and 0.75: the plurality of the three normal runs of
`ladder-{1,0,0.75}-2x-*`.

1. **T(x)** per endpoint, channel and stratum: the greys' deep medians at x = 0, 0.25, 1 (seven levels),
   0.75 (0, 128, 208, 255) and 0.5 (W42's), tabled per level against x, with the monotone range per
   position.
2. **The free side against x.** On every region of the w-test's support, and on every structured
   cell's declared free and lifted regions (`wtest.side_regions`) as a wider description:
   - M_x − C at each x where the cell was captured;
   - r(x) = (M_x − C) / (M₀.₅ − C), which the composite predicts as 2x on the free side;
   - the affine description M(x) = C + x·(W − C): M(0) − C, the slope, and the largest residual from
     the line through x = 0 and 1.

   The 0.25 values on the supported regions must equal `reading.json`'s; that is a consistency check, not
   a second read. **At x = 1 memo F declares the backdrop capture scale 0.125 on every shape** (against
   0.5 below 1), so W itself moves between 0.75 and 1. The x = 1 point is read through that and reported
   as such, never as a one-knob test.
3. **The x = 1 and x = 0 bodies.**
   - **x = 1:** M = W on both sides under LT, so the free and lifted excursions mirror each other. The
     mirror reading is m = (e_free + e_lifted) / (|e_free| + |e_lifted|), with e = M − C on each side of
     a two-level cell: 0 for any two-sided linear system, ±1 for a fully one-sided one. It is the
     region form of memo C's S = M(x) + M(x + pitch) (W42 grounding, probe §1), given at every x. Beside
     it, the step cells' profiles across the step (10–90 % transition width and the plateau levels) and
     the patch cells' core-against-ring contrast.
   - **x = 0:** the free side reads C directly (M(0) − C, predicted 0). The lifted side reads C with the
     hinge at the declared λ(0) = 0.675, reported as the implied (M(0) − C)/(M(1) − C) beside 0.675, with
     the x = 1 capture-scale caveat above.
4. **The five two-state cells** of G1b's bar (§5.199b §5): x = 0 receded 2x dark `b-p3-c64-rrect-md`, 2x
   light `a-g128-rrect-md` and `c-s32-hi-rrect-md`; x = 0.75 dark `a-g000-capsule-button__rest` and light
   `a-g128-rrect-md__inactive`. For each, both states' deep medians and every declared region's medians
   are given, the difference in codes is set against the bar (0.5 + 0.5 × the largest pairwise
   separation), and whether any w-test-supported region or T ordinate sees the split is stated.
5. **A recommendation** for the continuous slider's charter: a law in x or interpolated documents, and
   the fewest generations either needs. It is read off 1–3 and memo F's declared ramps.
