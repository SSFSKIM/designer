# W42 G0 — the instrument, proved to clause 2

The instrument stream of W42 G0 (charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`
v2.1, Design "The instrument (G0)", clause 2; ledger §5.194). It builds every reader the charter
names and proves each one before it may read Apple: on synthetic renders of every declared family
(proof 1), by separating the families that should be separable (proof 2), and on vitrea's own
canonical web captures, whose kernels the code states (proof 3). Everything is offline Python
(python3.12); no browser ran and **no native pixel was opened** — proof 3 reads only vitrea's web
captures of canonical calibration, validation and probe scenes.

**The tolerances were declared first.** `tolerances.json` was committed in `4c7a96c3`, with the engine,
before any proof output existed. No bar in it was loosened afterwards; every miss below is reported
as a miss.

**The bed is the declared one.** `bed.py` loads the bed stream's `scenes-w42-body.json` and `bed.json`
at w42-g0-bed `764217e1` (465 glass cells; SHA-256 pinned, read from that commit, or from `../bed/` once
G0 is integrated). The first proofs rendered on `5ba68aeb`'s cells; `07b45391`, `5d719b60` and `764217e1`
only ADD cells (the s = 32 receded rrect-sm rows; the rows the parent ruled from this stream's findings).
Rows of parts An, Aw, An_final, Aw_final, A_fix and E, the separation, null and refraction-order rows record
the pin they ran on; parts A, B and C (`7efe4ce8`) carry none and ran on `5ba68aeb`. The receded results are
final at `5d719b60` (the last pin adds active cells only) and the active ones at `764217e1`; every row the fix
wave of the review of `b151aff4` produced (`FIXES-b151aff4.md`) is at `764217e1` and carries the engine
label `fix-b151aff4`. H and the F bridges are never
rendered: the instrument is not tuned on the holdout's geometry.

## Files

| file | what it is |
| --- | --- |
| `tolerances.json` | the declared bars (clause 2), committed before any proof ran |
| `geometry.py` | the harness's backdrop generators replicated byte for byte (every committed canonical background, both scales), shapes, signed distances, t |
| `tone.py` | T: memo C's native-T table as the proofs' KNOWN transfer (G2 swaps in family A's curve), and vitrea's sRGB-affine transfer |
| `forward.py` | the forward engine: LT and every rival and rejected null as discrete choices of one model; the refraction-band mask; the decimated wide blur |
| `families.py` | the declared families with their parameter counts; k at its nested levels |
| `fitting.py`, `regions.py` | the bounded deterministic multistart (clause 6: LOCAL, equal weight per cell, lam inner per endpoint) and the region statistics clause 6 gates on |
| `bed.py`, `canon.py` | the declared bed (and its refraction exclusions); vitrea's canonical captures and the code's kernels |
| `read_model.py`, `read_mirror.py`, `read_heavy.py`, `read_esf.py`, `read_impulse.py`, `read_local.py`, `read_step.py`, `read_patch.py`, `read_depth.py`, `read_lambda.py`, `control_linear.py` | the statistic readers and the two-sided linear control |
| `ref_check.py/.json` | the engine against memo E's `lt.py`, the charter's named reference |
| `proof1_families.*`, `proof1_readers_a.*`, `proof1_readers_b.*` | proof 1 |
| `proof2_separation.*`, `proof2_nulls.*`, `proof_common.py` | proof 2 |
| `refraction_order.py` → `refraction_order.*` | the refraction-order test (the revised ruling 3): v3's two legs (`.v3`), v2's proof per pin, the first statistic's record (`.v1`) |
| `proof2_bleed_light.*`, `proof2_minimax_check.*`, `rerun_wshape_readers.py` | the fix wave's bounds on the literal bleed in light, the minimax convergence check, the W-shape reader re-runs |
| `i4_replay.*`, `i4_readers.py`, `i4_fitcontrol.py`, `i4_sections.*` | the id(cell)-key replay: every pre-token output re-evaluated with a token (finding I-4) |
| `FIXES-b151aff4.md` | the fix wave of the review of `b151aff4`: one entry per finding, what changed and what each re-run showed |
| `proof1_depth_sweeps.py` → `proof1_depth_{n,w}.*` | the active depth sweeps at either mask (descriptive depth reader); `proof1_depth_d34.*` its first run |
| `proof3_readers_a.*`, `proof3_readers_b.*` | proof 3 |
| `resolution.py` → `resolution.json`, `resolution.txt` | the resolution table, the separation table and the open pairs, assembled from the proofs' outputs |

Reproduce from this folder: `python3.12 geometry.py` (backdrop identity), `python3.12 ref_check.py`,
`python3.12 proof1_families.py`, `python3.12 proof2_separation.py`, `python3.12 proof2_nulls.py`,
`python3.12 proof1_readers_a.py <endpoints>`, `python3.12 proof1_readers_b.py <section>`,
`python3.12 proof3_readers_a.py <endpoints>`, `python3.12 proof3_readers_b.py`, then
`python3.12 summarize_a.py`, `python3.12 report_readers_b.py`, `python3.12 resolution.py`.

## The engine and the families

LT is memo E's algebra with its reference `lt.py`: the capture S = F ∗ B on R_fp (the box plus the
declared margin; F the 0.8-device-px floor, 1.6 on rrect-lg, before the knee); C = G(k·5·o(s, d,
pose)) ∗ S with the dump's exact opacity law; W = G(k·8) ∗ S on R_fp, clamp-to-edge when active and
normalised when receded; N = C ± λ·max(0, ±(W − C)); M = 0.5 N + 0.5 W; y = T(M) per channel. All
averaging is in encoded values; widths are in points. On memo C's cells it reproduces `lt.py`, which
interpolates five blur levels in depth
and this engine stays within 0.025 code rms (0.09 max) of a dense reference (`ref_check.json`, re-run on
the final engine: 0.0002–0.013 code rms when receded, from the decimated wide blur, and 0.01–0.11 when
active). Every family maps a
constant backdrop to T(level) to 1e-13 (clause 7 by construction). The decimated wide blur (≥ 12 device
px) is within 0.037 code of the direct filter everywhere on the bed.

| family | parameters per endpoint | differs from LT by |
| --- | --- | --- |
| LT | 2 (k, λ) | — |
| LT-2k | 3 | k_n and k_w |
| free-sn | 7 | σn a free span law (5 ordinates, flat in depth) |
| R1 | 2 | T on C and W before the fill |
| W-shape | 3 | W normalised on the rounded shape + margin μ |
| W-canvas | 2 | W (and C) on the whole canvas |
| W-tails | 4 | W = (1 − a) G(k·8) + a G(s2) |
| K2 | 3 | the knee against a second fill of width sk |
| C-linear | 2 | the narrow term averaged in linear light |
| knee-luma | 2 | the hinge decided on luma, applied to the whole colour |
| LT+bleed-lit-{pre,post} / -own-{pre,post} | 2 / 3 | the DECLARED bleed, dump-literal: radius k·0.35 s (or k_b), the bleed matrix with its saturation, darken (light) / normal (dark) at w = ob·r(d), r a ramp over the 0.35 s band, before or after T; rendered through the face that reproduces native T at family A's deep median |
| LT+bleed / LT+bleed-own | 2 / 3 | the bleed's Normal VARIANT, its assumptions stated (`forward.bleed_weight`): Normal mix in both schemes, pre-T, the whole shape, the matrix's affine part absorbed by native T |
| edge-swap | 2 | R_fp's edge modes swapped |
| rejected nulls | 2 each | the mixture reading; texel or device-px radii; R2; a literal box decimation |

**k at its nested levels:** one k for all four endpoints (1 + 4 λ = 5 parameters), one per scheme (6),
one per endpoint (LT-1k, 8), one per radius per endpoint (LT-2k, 12).

## The resolution table (condensed; every row, with its cells, is in `resolution.txt` / `.json`)

Gated: the family fitters and the step reader's support call (the parent's gating). Every other reader is
descriptive, its misses on record. Synthetic: proof 1's recovery error (bar); vitrea: proof 3 against the
float64 replica (bar), the superseded σ_RMS verdict in `resolution.txt`. Band: every active reader reads
outside the 20-pt band plus 2σn (the revised ruling 3's primary); the W-support reads are the fallback's.

| reader | status | quantity | synthetic | vitrea (replica) |
| --- | --- | --- | --- | --- |
| family fitters (LT, every rival) | gated | k, k_n, k_w; λ | ≤ 0.001 (0.005); ≤ 0.0008 (0.03), PASS | no counterpart |
| family fitters | gated | σn ordinates / μ / s2 / a / sk / k_b | 0.004 pt / 0.20 pt / 0.035 pt / 0.0005 / 0.013 pt / 0.0009, PASS | — |
| LT survival resolution | gated | k; λ | ±0.04–0.07; ±0.03–0.04 | — |
| LT against its rivals (estimates) | gated | \|k_n − k_w\|; sk; tail a; σn ordinate | ≈ 0.21–0.31; 3.0–4.0 pt; 0.11–0.15; 0.5–0.8 pt | — |
| step reader (D) | gated | support / edge call | canvas called when receded; box / shape / edge never called on D's centred steps | identical on 20/20, PASS |
| step reader | descriptive | σw on the true support | ≤ 0.07 % PASS | 1 miss (one-image identification) |
| mirror S (flagged) | descriptive | λ(1 − w) | ±0.002–0.010 PASS | values within 0.022; 3 flag calls differ, FAIL |
| per-cell λ (memo E) | descriptive | λ | ≤ 0.001 on identified cells PASS | light PASS (15 / 0), dark 6 miss, FAIL |
| patch and annulus (C) | descriptive | σn / σw (λ given) | ≤ 1.6 % / ≤ 5.0 % PASS | σn up to 9.3 %, σw 5–23 %, FAIL |
| model reader (memo C) | descriptive | σn / σw / λ / w | receded ±0.012 pt / ±0.008 pt / ±0.003 / ±0.001 PASS | FAIL (ill-conditioned on vitrea's graded share) |
| pitch-64 heavy reader | descriptive | σw | active 3.2 % PASS; receded 7.1 % FAIL | 7–192 % on 7/16, FAIL |
| ESF reader (memo B) | descriptive | narrow σ | 4.9–8.7 % FAIL (3 %) | FAIL (identified on one image only on 3 sides) |
| impulse reader (memo B) | descriptive | narrow σ | 3.5–9 % FAIL (3 %) | 1.8 %, PASS |
| depth-graded radius | descriptive | σn(d)/σn(centre) | light md d34 0.871 / 0.856, lg d60 0.870 / 0.876, lg d40 0.749 / 0.750, dark md 16/112 d34 0.868 / 0.856, PASS; dark 48/208 sweeps MISS | 3 pass / 10 miss |
| hinge-gap (memo E) | descriptive | λ per bin | ≤ 0.030 PASS | up to 0.30 (light 0.23), FAIL |
| known-space control | reported | λ, S in the wrong space | λ −0.5 … +1.6; S up to 0.43 | λ −0.50 … +1.54 |
| engine | — | interpolation; decimated W; invariance | ≤ 0.025 rms (0.09 max); ≤ 0.037 max; 1e-13 | — |

## Proof 1 — recovery on synthetic renders

Truths rendered through the memo C T stand-in, quantised ±0.5, on the declared cells.

- **The family fitters: every family, every endpoint, PASS** (`proof1_families.txt` part A, and at the
  narrow support on the final bed, parts An and An_final). k within 0.001 (bar 0.005), λ 0.0008 (0.03),
  the free σn ordinates 0.004 pt (0.05), μ 0.20 pt (1.0), s2 0.04 pt (2.0), a 0.0005 (0.03), sk 0.013 pt
  (0.25), k_b 0.0011 (0.05), every fit at the quantisation floor (pooled 0.33–0.45 code). R1 and the
  per-channel knee recover on the new rrect-lg rows too (An_final).
- **At the W support (the fallback's record)**: (parts Aw at `5d719b60` and Aw_final at `764217e1`, the 53.6-pt
  mask) LT, LT-2k, W-tails, K2, C-linear, both bleeds, edge-swap and W-canvas recover, and on the final bed
  R1 (3 cells) and the per-channel knee (2 cells) recover on the new rrect-lg rows. The free σn ordinates
  at s ≤ 96 run to their bound (no active cell of those spans survives the mask) and the s = 160 ordinate
  misses by 0.08–0.11 pt (bar 0.05); W-shape's μ misses by 2.0–3.5 pt (bar 1.0).
- **k's nesting** (part B, all four endpoints together): a global-k truth is recovered at every level
  (2.0497–2.0507 against 2.05). Memo E's per-endpoint k (1.983–2.094) read with ONE k misses region
  statistics by 1.23 codes (MARGINAL), with one k per scheme by 0.43 (UNRESOLVED); an LT-2k truth read by
  LT-1k leaves pooled 0.74, max cell 1.62. On region statistics (part E) the bed does NOT separate endpoint k
  values about 0.05 apart (the per-scheme level, whose light pair differs by 0.052, reads 0.43, UNRESOLVED), and
  a departure of about 0.07 reads only MARGINAL (1.23 at the global level, light-rest); within that range the
  tie-break keeps the more restricted k level.
- **Survival resolution of LT** (part C): k ±0.037–0.068, λ ±0.029–0.044 by endpoint.
- **Part A_fix** (the fix wave, pin `764217e1`): W-shape with C back on R_fp recovers μ within 0.14 pt in every
  endpoint; W-tails from a start off its truth (s2 28) within 0.47 pt / 0.005; the Normal bleed's k_b and
  free-sn's receded ordinates from starts off their truths within 0.004 and 0.007 pt. The four literal bleed
  forms recover k and λ in both schemes and k_b in dark; in light k_b is non-identifiable (the light bleed moves
  no pixel of the bed). These rows supersede the same family and endpoint in parts A / An.

## Proof 2 — separation

Truth family A rendered and quantised; family B fitted by least squares, refined by minimax on the
region statistics of A's exact render; s is B's best remaining miss. DISTINGUISHED above 1.5 codes,
UNRESOLVED below 0.5, MARGINAL between. Pairs not distinguished on their answering families are re-read
on the whole bed (both scales) before they are called.

- **Active, narrow support, final bed** (the primary): everything is DISTINGUISHED except the pairs below.
  C-linear 13–15 codes, knee-luma 16–18, the bleed's Normal variant 22 dark / 2.3 light, the dump-literal
  bleed in dark 6.1 / 11.0 (before / after T; own radius 5.5–10.9, its k_b at the 0.8 bound, so those s are
  upper bounds), R1 in dark 7.0–7.3, W-tails 2.6–2.8, W-shape at μ 4 2.0–3.0, LT-2k 2.1–2.5, K2 1.9–2.3,
  free-sn → LT 7.8–11.6 and LT → free-sn 2.2–2.7 (the depth grading is seen). Not distinguished: *R1 in
  light* (0.54–0.57 on the whole bed, with the new rrect-lg P5 / P3 rows in); *LT → LT+bleed-own in light*
  (1.28, the Normal variant: with its radius free, its light weight of at most 0.09 nearly vanishes into LT;
  the minimax search continued at three times its budget stays at 1.279); and *the dump-literal bleed in
  light*, both ways, every form (s ≤ 0.000 at the truth's own parameters, `proof2_bleed_light.txt`): its
  darken toward 0.9 + 0.1·sat(Bl) moves no pixel of the bed.
- **Active, the touched pairs at the W support (the fallback)**: the new rrect-lg rows keep answering
  cells. knee-luma is DISTINGUISHED both ways (2.6–3.2); R1 in dark reads 1.42 / 1.50 (marginal /
  distinguished) and in light 0.14; free-sn → LT is DISTINGUISHED (6.6–7.6) but LT → free-sn is MARGINAL
  (0.97–1.10 on the whole bed): under the fallback a flat span law nearly mimics the graded one, because
  only rrect-lg's 80- and 60-pt depths remain (o-law ratio 0.876).
- **Receded, final** (`5d719b60` whole-bed re-reads; every W-shape pair re-read at `764217e1` after the
  W-shape fix): W-shape against K2 or W-tails DISTINGUISHED both ways (whole bed 2.16–2.44 one way,
  1.68–3.09 the other; the review-era rows read 2.06–3.21); K2 against LT 1.60 / 2.06 and LT-2k 1.69,
  DISTINGUISHED; W-tails and W-canvas distinguished from every other U1 candidate (2.9–9.2); free-sn MARGINAL
  (1.17 at a 0.64-pt departure); R1 in light MARGINAL (0.51). The minimax searches of the near-line rows
  with three or more dimensions (K2 → W-tails 1.62 / 2.06, K2 → W-shape 1.68, W-tails → K2 1.81), continued
  at three times their budget, move by at most 0.022 (`proof2_minimax_check.txt`).
- **R1 in light, both poses**: an affine T commutes with the fill, and the stand-in T is nearly straight
  over 96–255 in light. Family A's greys 160–255 decide it: curved, and P5 / P3 separate R1; straight,
  and the order is non-identifiable by construction.
- **U3's active half** (W-canvas, edge-swap): non-identifiable on this bed (the parent's ruling 4);
  recorded, not re-read.
- **The rejected nulls** (`proof2_nulls.*`, LT truth, B/B′/C/D at both scales; re-run at the narrow mask
  in every active endpoint at `764217e1`, where the review-era rows had mixed the narrow and W masks): by the
  DECLARED pooled bar the unit nulls and R2 are **not refused** (texel 1.71–2.61, device px 1.17–1.41, R2
  1.71–2.84 against ≥ 4.65), and neither is the mixture reading in light active (2.56 against ≥ 2.60; it
  passes elsewhere, 2.78–4.13). Clause 2's stop makes each non-identifiable on this bed's synthetic proof.
  Their worst cells (texel 9.8–12.7, device px 8.5–10.1, R2 4.2–9.4, mixture 9.3) are a descriptive reading,
  not the declared refusal: at 2x a point is two device px and, off rrect-lg, one texel, so the 1x pass
  referees the unit in the sitting, and a pooled rms over a mostly-2x bed dilutes it (the 2x-only first run
  read the device-px null at 0.41, `proof2_nulls-2xonly.json`).

## Proof 3 — vitrea's own captures, against the float64 replica

Only vitrea's web captures are read. The parent's ruling 1 re-declared the bars (`b223600a`, before any
re-proof) as the difference between a reader's reading of the capture and of memo B's float64 replica of
the same cell, at the reader's proof-1 bar; the superseded σ_RMS bars and their misses stay in
`tolerances.json` and in every row's `vitrea_superseded`. 84 cells, both scales, all four endpoints (the
replica has no rrect-lg).

- **The gated step support call passes** (identical on 20/20). S's values agree within 0.022 wherever
  either image identifies them, but three identifiability calls differ (the capture's quantised residuals
  trip the flag's noise-floor check where the float replica does not); the per-cell λ, the patch widths
  and one step σw cell miss. Those readers are descriptive under the parent's gating.
- **Descriptive readers**: the single-width impulse reader passes (1.8 %); the model, heavy, ESF,
  two-Gaussian share, depth, hinge-gap and step-λ readings miss.
- **Disclosure (fork B, as reported):** it set its identifiability flags in code before the replica run,
  but after it had seen the superseded proof-3 results; the same call is made on both images.
- **The known-space control**: the ENCODED reading of vitrea's linear body manufactures λ from −0.50 to
  +1.54 on the capture and the replica alike, and S in the wrong space reads up to 0.43: the knee is
  established by S and every linear fit's loss, never by λ alone.
- **The family fitters have no vitrea counterpart** (a two-sided linear body with a share not 0.5 and a
  narrow width not k·5·o); their real-pixel counterpart is the model reader's algebra with w and λ free.

## The refraction band and the order test (the parent's revised ruling 3)

- **Primary: refraction acts AFTER the blur** in the active pose (vitrea's own order): a pixel beyond the
  band is the law's own value whatever the kernel's reach. Every active reader and family fitter uses the
  narrow-support mask d_in = 20 + 2σn,ref = 20 + 16.8 t pt (capsule and rrect-64 20, rrect-80 22.8, md
  25.6, rrect-112 28.4, ml 31.2, lg 36.8); receded keeps 8. Excluded from every active fit, with reasons
  (`bed.refraction_exclusions`): the d4 patches and the capsule S 16 patches (inside the band) and D's
  steps 8 and 16 pt outside rrect-md (inside the 19.2-pt outer reach).
- **The declared rival, BEFORE the blur, and its test** (`tolerances.json` `refraction_order_test`,
  `refraction_order.py`). The law is fitted at the narrow mask, its luma residual binned by depth, and
  Delta_c = rms(NEAR) − rms(FAR) taken per cell. The first statistic, the MEDIAN over structured cells
  minus the uniform cells' (declared `17da5c7d`), was proved and has no power (D ≤ 0.022 up to a 16-pt
  lens, `refraction_order.v1.txt`): before-the-blur contamination lives in the few cells whose band
  carries structure the deeper body lacks. Re-declared before its own proof (`cb490956`) on the TAIL: the
  mean of the 3 largest Delta_c over structured cells minus the same over uniform cells; BEFORE above
  0.30, AFTER below 0.15. *Disclosure (the review of `b151aff4`):* v1's own record, its carry counts (4 light
  and 3 dark structured cells with Delta_c > 0.30 at a 16-pt lens, none at 8 pt or less), was known when the
  tail form was chosen and already fixed the tail's outcome at the same 0.30 bar, so v2's proof confirmed
  what was known when v2 was declared. Its proof on the final bed (`refraction_order.txt`; `5d719b60`'s beside it
  reads the same): refraction after the blur reads D_tail +0.05 (AFTER) in both active endpoints;
  before the blur it reads AFTER up to a 4-pt lens (+0.05–0.06), 0.13–0.17 at 8 pt (AFTER dark,
  undecided light), and BEFORE at 16 pt (1.15–1.35), carried by B's pitch-64 cells on rrect-md. The
  test's resolution is therefore between an 8- and a 16-pt lens; below it the before-the-blur bias on the
  fit is small (k −0.017 / −0.018 and λ −0.009 at 8 pt, under LT's k survival resolution of ±0.04–0.07),
  and at 16 pt it reaches k −0.042 / −0.048. A weak lens before the blur is harmless to the fit; one
  strong enough to matter is caught. On Apple, a native depth trend that does not depend on backdrop
  structure is subtracted by the uniform cells; one that does (an unmodelled structure-dependent edge
  term) would read as BEFORE, which is why an undecided or BEFORE call goes to the parent before the
  fallback is taken.
- **v3, the conditional call** (declared in `79152643` before its proof; `refraction_order.v3.txt`). v2 had
  never rendered a wrong family without a lens, and it is not specific: a declared rival in the AFTER order
  reads BEFORE or undecided from LT's pooled rms 0.55 (LT-2k, both schemes). v3 fits LT as the gated fit
  (both scales, families A–E; 2x cells vote), keeps D_tail as S1, adds S2, the residual's projection on the
  stand-in lens's own regressor (Â, in pt), and admits a statistic only below P*, the pooled rms at which its
  specificity leg (every declared rival, no lens) first reads other than AFTER. Sensitivity: both read AFTER
  without a lens and BEFORE at 16 pt; at 8 pt S1 reads 0.14–0.18 and S2 6.5–6.6 pt (undecided); Â tracks the
  lens at about 0.8·A. Specificity: S1's P* is 0.55 light / 0.57 dark; S2 reads AFTER on every light rival up
  to the leg's top (P* 2.29, C-linear) and in dark fails first at 1.09 (R1, +6.4 pt), then on C-linear and the
  Normal bleed (+16–21 pt). **At memo E's LT residual on Apple's active cells (2.25 light, 3.45 dark), S1 is
  admitted nowhere, and S2 only in light, at the edge of its leg's range: with LT as the test family the
  dark-active order is undecidable before G2**, and light is decidable only if the fitted family's pooled rms
  on the new bed stays below 2.29.
- **Fallback**: if BEFORE wins on Apple's pixels, active fits use the 2σw mask (53.6 pt; rrect-ml and
  rrect-lg only). Its record is kept: parts Aw / Aw_final, the W-support separation rows
  (`resolution.txt`, the fallback table) and `proof1_depth_w.*`.
- **U3's active half** (the parent's ruling 4): non-identifiable on this bed, recorded; the tie-break keeps
  the declared box support in the active pose.

## The capture floor

Memo E's 0.8-device-px pre-blur (1.6 on rrect-lg) stays a declared constant, never fitted (the parent's
ruling). Its descriptive check is the literal box-decimation null against LT on the fine-pitch cells.
At the narrow-support mask on the final bed (`proof2_floor_check.txt`): in the active pose the null
misfits by 2.1 (light) and 3.1 (dark) codes pooled over the fine-pitch B′ cells, 6.0 and 8.9 on the worst
(the 1x pitch-4 capsule at its odd offset), so the bed tells the declared floor from a decimation where
the narrow term is the floor alone (t = 0, fine pitch); when receded it cannot (0.41–0.43 pooled: the
receded narrow blur, 4 pt and wider, swamps any floor). The check reads the form; it does not move the
constant. At the W support (the fallback) no active fine-pitch cell survives, and the null reads
0.42–0.44 (`proof2_nulls.txt`).

## Non-identifiable on this bed, declared before any fit

- U3's active half: canvas against R_fp, and R_fp's active edge mode.
- The box / rounded-shape / edge-mode call from D's centred steps (the step reader); the family fitters
  do separate W-shape at μ 4 on the whole bed.
- The depth law's 0.4t-at-1-pt end (nothing is readable shallower than the band plus 2σn).
- R1 in light, unless family A finds T curved over 144–255.
- Dark readings on the 48/208 levels at spans ≥ 96 under the stand-in T (the 16/112 twins read instead).
- Under the fallback only: the free σn ordinates at s ≤ 96 and the active rrect-md cells (no pixel beyond
  53.6 pt).
- The rejected nulls that miss their declared pooled bar on this bed's synthetic proof: radii in texels and
  in device px, R2 (every endpoint), and the mixture reading in light active. The 1x pass referees the unit.
- The dump-literal bleed in light (every form) and its k_b: it moves no pixel of the bed.
- The refraction order in dark active with LT as the test family (v3: no statistic is admitted at memo E's
  3.45 codes); in light it is decidable only below a pooled rms of 2.29.

## Bed questions, and how the bed answered them

1. U3's active half: recorded non-identifiable (`bed.json` `recordedNotCaptured`).
2. A readable second depth on rrect-md: the d34 patch (`5d719b60`); light active resolves md's grading.
3. Dark levels in dark T's compressed range: the 16/112 twins on md and ml, and a dark d34 twin
   (`764217e1`), which resolves dark md's grading (0.868 against 0.856; flat 0.998).
4. Box against rounded-shape support, receded: corner and capsule-end patches (`5d719b60`); the whole-bed
   re-read separates W-shape from K2 and W-tails, carried mostly by other rows.
5. Active R1, the per-channel knee and a gated depth pair under the fallback mask: P5 / P3 and E's pairs on
   rrect-lg and an S 8 at 60 pt (`764217e1`); each keeps answering cells under both masks (above).
6. Still open: the unit question is refereed only by the 1x pass (worst cells, not pooled rms).

## Engine defects found and fixed during the work

- **Memory**: blur caches bounded per cell and canvas-sized region masks let a fit over 50–90 cells hold
  12–20 GB per worker, and the machine's memory-pressure reaper stopped proof 2 once. Blurs now share one
  least-recently-used store bounded in bytes (`forward.BLUR_CACHE_BYTES`, 0.8 GB); populations are flat
  indices.
- **The store's key**: it was first keyed by `id(cell)`, so a new cell reusing a freed cell's id could read
  that cell's blurs when window, width and mode matched exactly (a trial reproduced the id reuse). It is
  keyed by a never-reused token since `04163eec`. The first version of this paragraph argued from the
  worst cells, which is false (30 pre-fix proof-2 rows have a worst cell of 3.0–12.8 codes). The evidence is
  now a replay (`i4_replay.txt`): every cited proof-2, null and floor row produced before or around the fix,
  re-evaluated at its recorded least-squares and minimax points by the code and pin that produced it with only
  the key made a token, reproduces its record exactly (81) or within the store's own width rounding (77; at most
  1.2e-4 code in s), which a fresh token-keyed fit replayed the same way also shows. No proof-2 row moved.
  **One reader output was contaminated**: `proof3_readers_b.replica.json` (`9c1623b4`). Its token-key replay
  differs on the checkerboard-8 / -64 λ rows over rrect-md / ml (a capture rms of 11.18 codes reads 0.77) and
  on two 1x checkerboard rrect-ml depth rows, and an audit of the same section with the original key logged 15
  hits whose stored blur came from another checkerboard pitch (25–255 codes). The token-keyed file replaces
  it; the contaminated one is kept as `i4_contaminated_proof3_readers_b.replica.json`. It moved the light
  per-cell λ replica reading from FAIL (14 pass / 1 miss) to PASS (15 / 0) and the light hinge-gap from 0.320
  (21 misses) to 0.230 (13), still FAIL. The other 39 reader files replayed clean: exactly or within the fit's
  own rounding, and where a file predates a reader revision, on every row `summarize_a.py` cites
  (`i4_sections.txt`; the one cited section that differs, the linear control, never reads the store).
- **W-shape's narrow term** followed W onto the shape window (up to 4.6 encoded codes on receded p16 cells at
  μ 4). C now stays on R_fp and only W moves; every W-shape row was re-run (above).
- **Part D's decimated-blur check** cleared only the cell's own cache after the shared store arrived, so its
  "direct" render read the decimated blurs back. With a fresh token it reads 0.0366 max / 0.0075 rms over 383
  cells, the value first recorded.
- **Trust selection** by the observed code truncated the dark knee side and biased λ to its bound; the fits
  use no truncation (the stand-in T is known everywhere) or the predicted input.
- **A k bound** of 4.0 voided three device-px null rows (their equivalent k is 4.1–4.2); widened to 9.
