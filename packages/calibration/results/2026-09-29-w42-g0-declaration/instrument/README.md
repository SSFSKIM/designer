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
at w42-g0-bed `07b45391` (pinned by SHA-256; read from that commit, or from `../bed/` once G0 is
integrated). Proofs 1–2 rendered on `5ba68aeb`'s cells; `07b45391` only adds the five s = 32 receded
rrect-sm rows, and proof 1 part E re-reads LT with them in (identical recovery). H and the F bridges
are never rendered: the instrument is not tuned on the holdout's geometry.

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
| LT+bleed / LT+bleed-own | 2 / 3 | the dump's active bleed (radius k·0.35 s or k_b·0.35 s, weight from its declared opacity and matrix) |
| edge-swap | 2 | R_fp's edge modes swapped |
| rejected nulls | 2 each | the mixture reading; texel or device-px radii; R2; a literal box decimation |

**k at its nested levels:** one k for all four endpoints (1 + 4 λ = 5 parameters), one per scheme (6),
one per endpoint (LT-1k, 8), one per radius per endpoint (LT-2k, 12).

## The resolution table (condensed; every row, with its cells, is in `resolution.txt` / `.json`)

Synthetic: proof 1's recovery error (bar); vitrea: proof 3 (bar). Band: where an active reader reads
relative to the 20-pt refraction band (receded has none).

| reader | quantity | synthetic | vitrea | band (active) |
| --- | --- | --- | --- | --- |
| family fitters (LT, every rival) | k, k_n, k_w | ≤ 0.001 (0.005) PASS | no counterpart | outside |
| family fitters | λ | ≤ 0.0008 (0.03) PASS | — | outside |
| family fitters | σn ordinates / μ / s2 / a / sk / k_b | 0.004 pt / 0.20 pt / 0.035 pt / 0.0005 / 0.013 pt / 0.0009, all PASS | — | outside |
| LT survival resolution | k; λ | ±0.04–0.07; ±0.03–0.04 (the move that shifts a statistic by 1 code) | — | outside |
| LT against its rivals | \|k_n − k_w\|; sk; tail a; σn ordinate | ≈ 0.21–0.37; 3–5 pt; 0.11–0.15; 0.5–0.9 pt (estimates) | — | outside |
| model reader (memo C) | σn / σw / λ / w, receded | ±0.012 pt / ±0.008 pt / ±0.003 / ±0.001 PASS | λ ≤ 0.12 on 48/58 FAIL; widths vs σ_RMS FAIL (replica: σn within 0.06 pt) | — |
| model reader | same, active t = 0 | σn FAIL on 1x p8 capsule (+0.25 pt); others PASS | as above | across |
| mirror S (flagged) | λ(1 − w) | ±0.002–0.010 PASS, all paths | ≤ 0.022 on flagged cells; 0.056 on all (FAIL as declared) | across (W) |
| mirror S, two-sided control | \|s1/gain\| | ≤ 0.0035 (0.024) PASS | — | — |
| pitch-64 heavy reader | σw | active 3.2 % PASS; receded 7.1 % FAIL (5 %) | group unrejected on 5 cells FAIL | across |
| heavy reader | support call, group rejection | PASS | no false footprint call | across |
| ESF reader (memo B) | narrow σ | 4.9 % active, 8.7 % receded FAIL (3 %) | 0.01–0.35 pt from the replica | outside |
| impulse reader (memo B) | narrow σ | 3.5–9 % FAIL (3 %); two-Gaussian on the linear control PASS | best-of 7.9 % PASS (10 %) | outside |
| patch and annulus (C) | σn / σw | ≤ 1.6 % / ≤ 5.0 % PASS (5 %) | σn with λ given ≤ 3 % on 6/20; λ free FAIL | outside (md S8/S32), across (lattices) |
| depth-graded radius | σn(d)/σn(centre) | light active lg 0.749 vs 0.750 PASS; md d24 0.811 vs 0.749 FAIL; dark non-identifiable | flat control 0.071 FAIL | outside (lg), across (md d24) |
| step reader (D) | σw on the true support | ≤ 0.07 % PASS | — | outside (out-steps excluded) |
| step reader | support / edge call | canvas called receded; box/shape/edge never called: non-identifiable on D | no false call; λ 2/20 FAIL | outside |
| per-cell λ (memo E) | λ | ≤ 0.001 on identified cells PASS (light 30/33, dark 11/33 identified) | ≤ 0.082 PASS | outside |
| hinge-gap (memo E) | λ per bin | ≤ 0.030 PASS | up to 0.71 FAIL | outside |
| known-space control | λ, S in the wrong space | λ −0.5 … +1.6; S up to 0.43 (reported) | λ −0.50 … +1.54 (reported) | — |
| engine | narrow interpolation; decimated W; invariance | ≤ 0.025 rms (0.09 max); ≤ 0.037 max; 1e-13 | — | — |

## Proof 1 — recovery on synthetic renders

Truths rendered through the memo C T stand-in, quantised ±0.5, on the declared cells.

- **The family fitters: every family, every endpoint, PASS** (`proof1_families.txt` part A). k to
  within 0.001 (bar 0.005), λ 0.0008 (0.03), the free σn ordinates 0.004 pt (0.05), μ 0.20 pt (1.0),
  s2 0.035 pt (2.0), a 0.0005 (0.03), sk 0.013 pt (0.25), k_b 0.0009 (0.05), each fit at the
  quantisation floor (pooled 0.35–0.45 code).
- **k's nesting** (part B, all four endpoints fitted together): a global-k truth is recovered at every
  level (2.0497–2.0507 against 2.05). Memo E's per-endpoint k (1.983 / 2.035 / 2.094 / 2.074) read with
  ONE k leaves a region-statistic miss of 1.23 codes (part E; MARGINAL), and with one k per scheme 0.43
  (UNRESOLVED). An LT-2k truth (1.75 / 2.10) read by LT-1k leaves pooled 0.74, max cell 1.62.
- **Survival resolution of LT** (part C: the move that shifts some region statistic by one code, λ
  re-fitted): k ±0.037–0.068, λ ±0.029–0.044 by endpoint.
- **The statistic readers** pass inside narrower scopes than their bars assumed, and miss several bars
  as declared: see the resolution table below and `resolution.txt`.

## Proof 2 — separation

Truth family A rendered and quantised; family B fitted by least squares, refined by minimax on the
region statistics of A's exact render; s is B's best remaining miss. DISTINGUISHED above 1.5 codes,
UNRESOLVED below 0.5, MARGINAL between (`tolerances.json`).

- **Distinguished**, both directions where both were run: C-linear (8–15 codes), knee-luma (10–18),
  LT + bleed (22 dark, 2.3 light), R1 in dark (2.5–7), W-canvas and edge-swap when receded (5.6–7.2),
  W-tails (2.6–3.5), W-shape at μ 4 (2.0–3.0), LT-2k (2.1–2.5), K2 when active (1.9–2.3), the free
  σn(span) law when active (7.8–11.5) and dark receded (1.6), and LT against free-sn when active
  (2.2–2.7: the depth grading is seen beyond the band).
- **Not distinguished, and what would separate them** (`resolution.txt`, PAIRS NOT DISTINGUISHED):
  - *W-canvas and edge-swap in the ACTIVE pose* (0.01–0.8): non-identifiable on this bed. The active
    margin keeps R_fp's edge ≥ 45 pt from every readable pixel, and D's steps outside the edge, the
    answering rows, are refraction-confounded. No cell inside the canvas and outside the 19.2-pt reach
    answers U3's active half.
  - *R1 in light, both poses* (0.5): an affine T commutes with the fill, and the stand-in T is nearly
    straight over 144–255. Family A's greys 160–255 decide it: curved, and B's P5/P3 separate R1;
    straight, and the order is non-identifiable by construction.
  - *K2 when receded* (1.24–1.37 at sk 12 against 8k = 16.3 pt), *LT-2k light receded* (1.40 at
    Δk 0.35), *free-sn light receded* (1.02 at a 0.64-pt departure): marginal at the truths chosen;
    the estimated resolution rows give the departure each would need.
  - *W-shape against K2 or W-tails when receded* (0.83–0.86): the shape support differs from the box
    only near corners and capsule ends. Structure placed there (a step or a patch within ~16 pt of an
    rrect corner or a capsule end, receded) would separate them: a bed question.
- **Estimated resolutions** (linear in the departure, from each pair's s): |k_n − k_w| 0.21–0.37;
  K2's |sk − 8k| 3–5 pt; a 40-pt tail's weight 0.11–0.15; a free σn ordinate 0.5–0.9 pt.
- **k's levels:** memo E's per-endpoint spread (1.983–2.094) read with one global k misses region
  statistics by 1.23 codes (MARGINAL), by 0.43 with one k per scheme; LT's survival resolution in k is
  ±0.04–0.07. The bed separates endpoint k values that differ by more than about 0.05, not less; below
  that the tie-break (parameter count) keeps the global k the parent expects primary.
- **The rejected nulls** (`proof2_nulls.*`, LT truth, B/B′/C/D at both scales): the mixture reading
  PASSES memo E's bar (pooled 2.68–4.61 ≥ 2.60). The texel null FAILS the declared bar (pooled
  1.85–2.77 against ≥ 4.65) though it misses some cell by 9.8–12.7 codes. The device-px null is valid on
  light active only (pooled 1.46, max cell 8.93: FAIL as declared); on the other three endpoints its fit
  sat on the shared k bound of 4.0, where the device-px equivalent of memo E's k is 4.1–4.2, so those rows
  overstate its misfit and are void (the bound is widened to 9 for the resume). At 2x a point is two
  device px and, off rrect-lg, one texel, so only the 1x pass referees the unit, and a pooled rms over a
  mostly-2x bed dilutes it: the 2x-only first run (`proof2_nulls-2xonly.json`) read the device-px null at
  0.41 on light active, indistinguishable from LT. R2 read 1.73 pooled (4.27 max) on light receded, FAIL
  as declared; its other endpoints and the box-floor null did not run (below).

## Proof 3 — vitrea's own captures

Only vitrea's web captures are read. Truth: the code's kernels (memo B's code map: body chain L1,
σ_RMS 1.58 device px; deep L4 or the dark chain LOD; the share per span and depth) and, where the
kernel is not Gaussian, memo B's float64 replica of the renderer.

- **The pixel-level resolution is small**: on the 1x cells read both ways (`resolution_rows_a.json`, the
  replica row), capture and replica agree to 0.00–0.06 pt in the model reader's narrow width, 0.01–0.13 pt
  in the impulse reader's, and 0.01–0.35 pt in the ESF reader's (most within 0.09).
- **The bars against the code's σ_RMS fail as declared for most readers, and the replica shows why:
  model mismatch, not pixels.** A Gaussian reader of the L1 chain reads +6–7 %, the platykurtic L4 reads
  wide, and vitrea's share is depth-graded. The model reader's λ is ≤ 0.12 on 48 of 58 cells (FAIL on
  10); its σn misses by 20–28 % on the 1x pitch-64 cells (the replica reads the same) plus one degenerate
  fit, and its σw by up to 128 %; the mirror S reads ≤ 0.022 on the 11 cells its flag
  identifies but 0.056 over all 50 (FAIL as declared); the heavy reader leaves the group mean
  unrejected on 5 cells; the hinge-gap reader reads per-bin λ up to 0.71 on a body with no knee (FAIL);
  the step reader's λ misses on 2 of 20 cells. The impulse reader (7.9 %), the per-cell λ reader
  (≤ 0.082), the patch reader with λ given, and every support call (no false footprint call anywhere)
  pass.
- **The known-space control**: the ENCODED reading of vitrea's linear body manufactures λ from −0.50 to
  +1.54 (memo C read 1.4–1.5), and S in the wrong space reads up to 0.43. The knee is established by S
  and by every linear fit's loss, never by λ alone.
- **The family fitters have no vitrea counterpart**: vitrea draws a two-sided linear body whose share
  is not 0.5 and whose narrow width is not k·5·o. Their real-pixel proof is the model reader's, which
  is the same algebra with w and λ free.

## The refraction band (the parent's ruling on the bed stream's finding)

Active regions sit beyond the 20-pt inner band plus the narrow kernel's support: the engine's active
deep mask is d_in = 20 + 2·σn,ref = 20 + 16.8 t pt (capsule and rrect-64 20, rrect-80 22.8, md 25.6,
rrect-112 28.4, ml 31.2, lg 36.8); receded keeps 8. Excluded from every active fit and listed with
its reason (`bed.refraction_exclusions`): the d4 depth patches and the capsule S 16 patches (inside
the inner band) and D's steps 8 and 16 pt outside rrect-md (inside the 19.2-pt outer reach). The band
column of the resolution table says, per active reader, whether it reads outside, across or inside.

**The support in "20 pt plus the kernel's support" is read two ways, and the parent should rule.** The
engine and the narrow readers add the NARROW kernel's support (2σn). Fork A's W readers (model σw, S,
heavy) add the WIDE kernel's (2σw, 51.7–53.5 pt), which leaves active W readable only on rrect-ml and
rrect-lg. Which is right depends on whether Apple refracts the capture before the blur (then deep pixels
integrate refracted content over W's reach) or displaces the output after it (then only the band's own
pixels are confounded); the dumps give an input order, not an algebra.

## What clause 2's stop means for G2

- **Read Apple, gated:** every family fitter (LT and every rival, every parameter at its bar); S with its
  identifiability flag (synthetic ±0.002–0.010 on every path; ≤ 0.022 on the vitrea cells the flag
  accepts); the per-cell λ reader; the patch reader's widths with λ given; the step reader's σw and its
  support call (no false call on vitrea).
- **Do not read Apple as gated readers** (a proof-1 or proof-3 miss, clause 2's stop; their quantities are
  carried by the family fitters, which pass): the model reader (its synthetic reads pass on receded and
  t = 0 cells, but proof 3 misses λ on 10 of 58 cells and its widths against σ_RMS); the heavy reader
  (receded σw 5.4–7.1 %; proof 3 leaves the group unrejected on 5 cells); the hinge-gap reader (fails its
  vitrea control; memo E's "flat 0.68–0.72" lies within its synthetic spread); the ESF reader (4.9–8.7 %
  against 3 %: W's slope over half a cell biases it wherever σn > 2.5 pt); the single-width impulse reader
  under LT (3.5–9 %: its core is 0.5 C + 0.5 W); the depth reader (it resolves only light active rrect-lg,
  0.749 against 0.750, and misses its vitrea flat control by 0.071); the patch reader with λ free. Where a
  proof-3 miss is model mismatch (the replica reads the same), a bar re-declared against the replica,
  before a re-proof, is the parent's call.
- **Non-identifiable on this bed, declared before any fit:** U3's active half (canvas against R_fp, and
  R_fp's active edge mode); the box/shape/edge-mode call from D's centred steps; the depth law's
  0.4t-at-1-pt end (nothing is readable shallower than 25.6 pt on md or 36.8 pt on lg); dark-active
  depth grading and every dark reader at spans ≥ 96 under the stand-in T (family A's dark 160–255
  ordinates lift this if Apple's T keeps slope there); R1 in light unless family A finds T curved over
  144–255.

## Bed questions for the parent

1. U3 active has no answering cell (above). Recorded as non-identifiable; the bed stream's report
   reached the same conclusion.
2. rrect-md's depth sweep: its s/4 patch (depth 24) is cut by the band mask; a patch near 34 pt depth
   (content 30–38, o-law ratio 0.85) would give md a readable second depth.
3. The dark passes' C, D and depth levels (48/208) put the bright side in dark T's compressed range at
   spans ≥ 96 under the stand-in; a pair like P4's 16/112 would read there unless family A shows usable
   slope above 128.
4. Box against rounded-shape support, receded: structure within ~16 pt of an rrect corner or a capsule
   end is what would separate W-shape from K2 and W-tails and let the step reader call the support.
5. The unit question (points against device px or texels) is refereed by the 1x pass alone; it does so
   on its worst cells (texel 9.8–12.7 codes, device px 8.9 on light active) but not in pooled rms. More 1x
   structure, or a statistic read per scale, would make it a pooled result.

## Runs stopped by the machine's memory pressure (not restarted)

Proof 2's last runs were stopped by Claude Code's memory-pressure reaper while the session was idle; the
instruction attached to that stop is not to restart them without being asked. The cause is found and
fixed in the engine: blur caches were bounded per cell (160 blurs), so a fit over 50–90 cells at 2x held
12–20 GB per worker; they are now one least-recently-used store bounded in bytes per process
(`forward.BLUR_CACHE_BYTES`, 0.8 GB), values unchanged. What did not run:
- the U1 cross-pairs when receded: K2 and W-canvas as truths in light receded, and all twelve in dark
  receded;
- the whole-bed re-reads of every pair not distinguished on its answering families (`proof2_separation.py`
  re-reads them on the whole bed, both scales, before calling a pair unresolved);
- the rejected nulls null-R2 (three endpoints) and null-boxfloor (all four) on both scales, and the
  device-px null on the three endpoints where the k bound voided it.
Resume with `W42_POOL=2 python3.12 proof2_separation.py rivals lt u1` (it skips every pair already in
`proof2_separation.json`) and `python3.12 proof2_nulls.py`, then `python3.12 resolution.py`.
