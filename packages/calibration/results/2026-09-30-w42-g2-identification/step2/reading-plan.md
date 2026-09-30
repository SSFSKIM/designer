# W42 G2 step 2 — the reading plan, committed with the pins before the first archive read (2026-10-01)

Governed by the charter (G2 step 2; clauses 6 and 15; Decision Logs 3 and 5a–5f), the hashed
declaration (`f04ae95b…`, every item) and the two pre-read addenda pinned in `pins.json`. This note
adds no family, parameter, level or bar. It states, before any archive pixel is opened, the
operational readings the declared path leaves to the reader, each with its reason, so none of them
is chosen after seeing Apple's pixels. Where this note and a declared text could be read
differently, the declared text governs and the difference is reported.

1. **What is read.** Roles calibration and validation only, through the wave's guarded Reader, with
   `~/vitrea-w42/g1` denied by the archive module's audit hook in every reading process. H is never
   requested; F (probe) is not needed and is not read.
2. **The observed image of a cell** is the plurality frame over its seven normal-protocol runs
   (ties to the earliest run). The bar is 0.5 on every statistic and G1's state check moved no
   region median between states, so the region statistics do not depend on this choice; the
   per-pixel least squares does, and the plurality is W39's published state.
3. **Channels.** Every cell is read in RGB and every channel is required. A grey-backdrop cell
   (families A–D) is rendered by the instrument on its luma, which equals each channel, and passes
   through the per-channel native T, T_c(M) for c in R, G, B: `compose` is evaluated once per
   channel with that channel's scalar T and stacked, so every declared family (the literal bleed's
   face included) runs unedited.
4. **Native T.** Per endpoint and channel, `implementation-design/native_t.py` (the addendum's
   executable form) over the 2x calibration family-A deep medians (`regions.statistics`,
   population `deep`, on the cell's own deep mask): capsule → the t = 0 stratum (64), rrect-80 → 80,
   rrect-md → 96, rrect-ml → 128, rrect-lg → 160. A cell reads T(L, s) at its own span. Measured
   ordinates are checked for monotonicity per stratum and channel. A decrease is recorded as a
   finding for the parent and never repaired: the forward curve still passes through every
   measured ordinate as measured, and the addendum's guard acts only on completed grid points.
5. **The structure fit** (the gated fit, clause 6). Per family and endpoint, on the endpoint's
   calibration cells of families B, B′, C and D at both scales, at the declared mask (active: the
   narrow mask; receded: 8 pt). Family A's calibration cells are left out of the optimisation
   only: every family maps a constant backdrop to T(level) (the engine: 1e-13), so they add a
   parameter-free constant and change no optimum; they are scored. Least squares per
   `fitting.Problem` (equal cell weight, λ inner by golden section on [−0.5, 1.6], outer
   parameters by bounded Powell or bounded Brent from `proof_common.starts_for`, LOCAL), then
   minimax on the region statistics against Apple's, the outer parameters and λ together by
   Nelder–Mead from the least-squares point (`proof_common.minimax_refine`'s method). In the
   minimax a censored native statistic (≤ 5 or ≥ 250, X21) enters one-sidedly as its rail
   deficit, W41 G1's reading (`body41.score`).
6. **Family E, the knee form and candidate 2's chroma scale.** On grey backdrops the three knee
   forms coincide exactly, so family E alone answers the knee. With the family's k and λ held at
   its grey fit, each form is read through candidate 2's declared chroma form
   y_c = T_c(L(arg)) + s·g(L(arg))·(arg_c − L(arg)), clipped to [0, 255], with arg = M_rgb
   (per-channel), the whole-colour on-luma composite, or M_L + (W − L(W)), and g W41 G1's E3 fit
   for the endpoint. s is fitted on E's calibration cells (least squares, then minimax) and
   checked on its validation cells. Per-channel T on E alone would carry the backdrop's chroma at
   T's own slope, which is not a declared chroma for Apple, so it is not used for the knee.
7. **Survival** (clause 6): every region statistic and channel of every calibration and validation
   cell, at max(1 code, bar) with the bar read from G1's `bar.json.gz` per cell, statistic and
   channel. Statuses as `body41.score`: native in (5, 250) is measured and passes within the
   bound; native ≤ 5 requires the prediction ≤ 5 and native ≥ 250 requires it ≥ 250
   (censored-bound-satisfied), otherwise UNMEASURED and a failure. A cell with no statistic (the
   1x pitch-4 checkers: every population under 12 px) is UNMEASURED and neither passes nor
   fails. A family survives an endpoint only if nothing fails; it is scored at its minimax point
   and at its least-squares point, and either point surviving is a survival.
8. **"Beats" and resolution.** Family B beats family A at an admitted discriminator (a measured
   statistic, native in (5, 250), of a calibration or validation cell) if |e_A| − |e_B| exceeds
   max(3, bar_A + bar_B); two families are within resolution if their predictions differ by less
   than that at every admitted discriminator (W41 G1's `report.py` form). The k ladder
   (`kNesting`) takes a less restricted level only where it beats the more restricted one.
9. **The width unit.** LT is fitted in points, texels and device px on the same cells; the 1x
   cells decide (`rejectedNulls`): a unit is taken over points only if it beats points at an
   admitted 1x discriminator; otherwise the declared points stand.
10. **The refraction order**, v3 exactly as declared: the test family (the clause-6 survivor, or LT
    if none) fitted on families A–E, calibration and validation, both scales, the narrow mask,
    with the instrument's own per-channel output on E; P, S1 over the 2x voters, S2, admission
    against P*. With no call, Decision Log 5f: the family is fitted on the endpoint's calibration
    cells under the narrow mask and under the 53.6-pt mask, and the two agree only if every fitted
    parameter's difference lies within its survival resolution (`resolution.json`; for another
    family, computed by the same rule before the comparison).
11. **Scale of work, and stops.** Every declared rival is fitted with its declared count, in each
    endpoint where it is defined (the bleeds are zero when receded and identical to LT there). No
    family, form or parameter is added after the first read; a result that tempts one is recorded
    as a finding for the next wave.
