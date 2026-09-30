# W42 G0 instrument: the fix wave of the review of `b151aff4`

One entry per finding of the instrument review, each with the parent's disposition
(`w42-g0-review-dispositions.md`), what changed, what each re-run showed, and the lines the parent folds into
§5.194 and the declaration. Branch `w42-g0-fix-instrument`, off `9a695ec0`. Every re-run is at bed pin `764217e1`
and carries the engine label `fix-b151aff4`. From the coordinator's throttle onward, the runs went one proof
script at a time (`W42_POOL=2`, BLAS threads 1). `freeze.py verify` reads 1,818.

## Summary

- **I-1, the refraction order: undecidable in dark active before G2.** v3 was declared (`79152643`) and then
  proved (`0b9e8940`). Two statistics were tested, D_tail (S1) and a lens-matched projection (S2):
  - both are sensitive, reading BEFORE at a 16-pt lens and undecided at 8 pt;
  - S1 is specific only below a pooled rms of 0.55–0.57;
  - S2 is specific up to 2.29 in light (the top of its leg) and only up to 1.09 in dark.

  At memo E's LT residual on Apple's active cells (2.25 light, 3.45 dark), no statistic is admitted in dark,
  and in light only S2 is, at the edge of its leg. The parent should take the dark-active refraction order
  to the user as undecidable before G2.
- **I-2, W-shape.** C is back on R_fp and every W-shape result was re-run. **No verdict changes**; receded
  W-shape against K2 / W-tails reads 2.16–2.44 on the whole bed (was 2.24–2.59).
- **I-3, the bleed.** The dump-literal bleed is now the declared form, and the old one is a stated variant.
  In dark it is DISTINGUISHED from LT (5.5–11.0). **In light it moves no pixel of the bed**, so under the
  literal reading it cannot be light-active U7's cause.
- **I-4, the id(cell) key.** 158 proof-2, null and floor rows were replayed at their recorded points with a
  token key. **None moved**. But **one reader output was contaminated** (`proof3_readers_b.replica`,
  replaced): the light per-cell λ replica reading is now PASS. The remaining reader replays are still running.
- **I-6, the nulls.** Re-run at the narrow mask, the unit nulls, R2 and now the light-active mixture are
  **not refused** by their declared bars. They are recorded as non-identifiable.
- **I-8, minimax.** The continued searches moved s by at most 0.022; no verdict changes.
- **I-5, I-7, I-9 and I-10** are done as disposed.

## I-1 (major): the refraction-order test's specificity

**Disposition.**
- Add a specificity leg.
- Declare which scales vote.
- Make the call valid only where the leg reads AFTER below 0.15, else UNDECIDED and the question goes to the
  user.
- Disclose that v1's carry counts had fixed the tail's outcome.

**Changed.**
- `tolerances.json` `refraction_order_test.v3_2026-09-30` was committed in `79152643`, before any v3 proof ran.
  - The test family F (LT here) is fitted as the gated fit: both scales, families A–E, narrow mask.
  - Only 2x cells vote. The 1x cells are fitted but hold a quarter of the pixels, and memo E's 1x aliasing
    misfit is graded in depth.
  - **S1** is D_tail, unchanged, with BEFORE > 0.30 and AFTER < 0.15.
  - **S2** is new: the pooled projection of the voting structured cells' luma residual on the regressor
    R_c = F rendered with the stand-in lens (A_ref 8 pt) before every blur, minus F rendered without it.
    Â = 8·β, with BEFORE ≥ 8 pt and AFTER < 4 pt.
  - The specificity leg renders every declared rival (the literal bleeds included) as an AFTER truth with no
    lens and fits LT.
  - Each statistic is admitted only below P*, the smallest pooled rms at which its leg reads other than AFTER.
    If the leg never does, P* is the leg's top.
  - Neither statistic admitted → UNDECIDED, and the question goes to the user.
- The v2 disclosure sits beside v2 in `tolerances.json` (`v2_disclosure_2026-09-30`) and in the README.
- `refraction_order.py` runs both legs (`refraction_order.v3.*`). The v2 record is kept as it was.

**Re-run (`0b9e8940`, `refraction_order.v3.txt`).**

Sensitivity leg (an LT truth with the lens before the blur):

| lens A | S1 light / dark | S2 (Â) light / dark |
| --- | --- | --- |
| 0 | +0.052 / +0.051 AFTER | +0.01 / +0.01 pt AFTER |
| 2 pt | +0.051 / +0.051 | +1.37 / +1.27 |
| 4 pt | +0.062 / +0.051 | +3.21 / +3.03 |
| 8 pt | +0.176 undecided / +0.135 AFTER | +6.53 / +6.61 undecided |
| 16 pt | +1.368 / +1.162 BEFORE | +13.57 / +13.12 BEFORE |

- Both statistics have a resolution of 16 pt. Â estimates the lens at about 0.8·A.

Specificity leg (a rival as the truth, LT fitted; P is LT's pooled rms). Rows reading other than AFTER:

| scheme | S1 | S2 |
| --- | --- | --- |
| light | LT-2k +0.26 (P 0.55), W-tails +0.29 (0.74), knee-luma +0.34 (1.29), C-linear +1.00 (2.29) | none; every rival AFTER, the top of the leg is P 2.29 |
| dark | LT-2k +0.34 (0.57), free-sn +0.21 (0.92), R1 +0.53 (1.09), knee-luma +0.16 (1.10), the literal bleeds +2.4 to +3.5 (1.07–1.64), C-linear +1.34 (1.63), the Normal bleed +1.56 to +1.60 (2.29–2.33) | R1 +6.44 (1.09), C-linear +20.8 (1.63), the Normal bleed +16.2 to +16.5 (2.29–2.33) |

- S2 reads the literal bleeds AFTER (−1.3 to −1.5 pt), although S1 reads them BEFORE.

**Result, stated plainly.**

| | S1 P* | S2 P* |
| --- | --- | --- |
| light | 0.549 | 2.285 (the leg's top; no false call) |
| dark | 0.568 | 1.086 |

- Memo E's LT pooled rms on Apple's active cells is 2.25 light and 3.45 dark (memo E §2f).
- With LT as the test family, **no statistic is admitted in dark active**, so the dark-active order is
  UNDECIDED before G2.
- In light, S2 is admitted only if F's pooled rms on the new bed stays below 2.29. Memo E's 2.25 sits at the
  edge of the leg's range, where the admission rests on one rival (C-linear, P 2.29, Â −2.7).
- No conditioning among those declared makes the test both sensitive and specific at Apple's expected
  residual in dark. The call could be made only if the family that survives clause 6 fits Apple's active
  cells below about 1.1 codes (S2) or 0.55 (S1).
- `validity()` flags admission against a single 2.1-code line. The per-endpoint reading above, against memo
  E's 2.25 / 3.45, is the one to carry.

**For the parent to fold.**
- §5.194 §4 and `declaration.md` `refractionOrder`:
  - v3 replaces the v2 call;
  - the disclosure goes beside v2;
  - "the test resolves between an 8- and a 16-pt lens" becomes "a 16-pt lens reads BEFORE; an 8-pt lens reads
    undecided";
  - the user question: the dark-active order is undecidable before G2.
- `declaration.md` `nonIdentifiable`: the dark-active refraction order with LT as F.

## I-2 (major): W-shape moved the narrow term's support

**Changed** (`f0861bac`, `forward.maps`).
- C (and the bleed) stay on `crop('box')`, as LT's do and as `read_local` takes them. Only W moves to the
  rounded-shape window, with its normalising weight.
- The weight's store key is its content (`('shape', mu)`), not `id(weight)`.
- C for W-shape is now bit-identical to LT's C. The families whose model did not change render
  bit-identically to `9a695ec0`'s engine: LT, LT-2k, W-tails, K2, C-linear, W-canvas, edge-swap, R1, free-sn
  and both Normal bleeds, checked on 6 cells in each of light-rest and dark-inactive.

**Re-runs.**
- **Part A_fix** (`e7b767da`): μ is recovered within 0.14 pt in all four endpoints (bar 1.0). All PASS, pooled
  0.40–0.44.
- **Proof 2, the receded U1 set and LT↔W-shape** (`7ef9afdd`). "Whole" rows are whole-bed re-reads; "subset"
  rows were distinguished on their answering cells and not re-read.

  | pair (light / dark receded) | before | after |
  | --- | --- | --- |
  | W-shape → K2 (whole) | 2.24 / 2.28 | 2.16 / 2.19 |
  | W-shape → W-tails (whole) | 2.25 / 2.59 | 2.22 / 2.44 (light fit at its a bound) |
  | K2 → W-shape | 2.63 / 3.21 (whole) | 2.68 (whole) / 1.68 (subset; minimax-checked 1.678) |
  | W-tails → W-shape | 3.05 / 3.12 | 3.09 / 2.96 |
  | W-shape → LT | 2.21 / 2.32 | 2.20 / 2.42 |
  | LT → W-shape | 2.38 / 2.49 | 2.36 / 2.67 |
  | W-shape → W-canvas | 6.91 / 6.81 | 6.84 / 6.88 |
  | W-canvas → W-shape | 0.06 / 0.06 | 0.34 / 0.44, UNRESOLVED (containment, as before) |

  - Active W-shape → LT is unchanged: 1.96 / 2.98.
  - **Every verdict holds.**
- **Reader rows with a W-shape truth** (`6d824e98`):
  - the gated step support call still reads no call (gap 0.0005, PASS, 13 D cells);
  - the U1 λ diagnostic's W-shape drifts move by at most 0.04 (light ±0.03; dark md P1 −0.44).
- **Not re-run.** The two active LT → W-shape rows (s 0.01, μ at its bound: W-shape contains LT there). They
  are marked STALE in `resolution.txt`. The reviewer measured the active C change at ≤ 0.01 code.

**For the parent to fold.** §5.194 §3's receded numbers ("W-shape against K2 and W-tails 2.06–3.21") become
the table above.

## I-3 (major): the bleed rival's undeclared choices

**Changed** (`f0861bac`, `forward.py` "the dump-literal bleed"; `families.py`).

The declared form takes every bleed input memo D records (`w42-dumps.txt` lines 128, 135 and 144–146):

| input | the literal reading |
| --- | --- |
| radius | 0.35 s, scaled by k (shared, or its own k_b) |
| colour | Q = black + (white − black)·sat(Bl) on encoded values (0.9 / 1 / 1.2 light, 0.125 / 0.5 / 1 dark) |
| blend | darkenBlend: a darken in light, a normal blend in dark |
| weight | w = ob·r(d), ob = 0.5t light, 0.8t dark |
| band (assumed) | height 0.35 s read as the band's depth, and distances 1/0 as the ramp's ends in units of the height: r = 1 at the edge, 0 at one height inward |
| amount | equal to the height in every dump, so it enters as the same extent; no displacement is modelled |
| place | before T or after T, a discrete choice |

- **Families:** LT+bleed-lit-pre / -post / -own-pre / -own-post.
- **Native T is preserved at family A's deep median:** each form renders through the face whose uniform
  response reproduces native T there.
- **The old form is kept as a stated variant**, LT+bleed / LT+bleed-own. Its stated assumptions sit beside
  `forward.bleed_weight`:
  - a Normal mix in both schemes;
  - before T;
  - the whole shape at one weight;
  - the matrix's affine part absorbed by native T;
  - the saturation not taken.

**Re-runs.**
- **Recovery (part A_fix).** k and λ recover in both schemes; k_b recovers in dark (±0.0004). In light k_b is
  non-identifiable (4.0 at the bound, 2.55) because the light bleed has no effect.
- **Light** (`proof2_bleed_light.txt`, whole bed B–E, both scales):
  - the literal forms move no pixel by more than 0.000 codes before T and 0.024 after;
  - all eight light pairs are bounded at s ≤ 0.000 at the truth's own parameters: UNRESOLVED, non-identifiable.
- **Dark separation** (`7ef9afdd`), DISTINGUISHED both ways:

  | form | rival → LT | LT → rival |
  | --- | --- | --- |
  | pre-T | 6.13 | 6.13 |
  | post-T | 10.99 | 11.00 |
  | own radius, pre-T | 6.09 | 5.45 |
  | own radius, post-T | 10.89 | 9.37 |

  The two own-radius LT → rival fits sit at the k_b bound 0.8, so those s are upper bounds.
- **Part D invariance:** every literal form keeps the deep median to 3e-14 and departs per pixel by up to
  7.3 codes (pre-T) or 9.5 (post-T) inside its band in dark.
- **The Normal variant** keeps its record: 22 dark and 2.3 light; LT → LT+bleed-own light 1.28 (MARGINAL,
  minimax-converged).
- **In the refraction leg,** the literal dark bleeds read S1 BEFORE (+2.4 to +3.5) and S2 AFTER.

**For the parent to fold.**
- §5.194 §3 and `declaration.md` `rivals`:
  - the bleed row becomes the four literal forms (2 or 3 parameters) plus the Normal variant with its
    assumptions;
  - the "1.28 light / 22 dark" figures are the variant's.
- `nonIdentifiable`: the literal light bleed and its k_b.
- **U7, and the gate's light-active failure source:** under the dump-literal reading the bleed cannot supply
  light-active structure on this bed. If U7 is a bleed at all, it is only under the Normal variant's
  assumptions.

## I-4 (minor): the id(cell) argument replaced by evidence

**Changed.** The README's worst-cell argument is replaced by a replay (`i4_replay.py`, `i4_readers.py`,
`i4_fitcontrol.py`, run by the fork). Each output is re-evaluated at its recorded points, with no refit, by
the code and pin of the commit that produced it; only the store's key is changed to a never-reused token.

**Result (`bdf6ec85`, `i4_replay.txt`).** 158 rows were replayed (110 pairs, 20 nulls, 20 2x-only nulls,
8 floor rows):
- 81 reproduce their record EXACTLY;
- 77 agree within the store's own width rounding: at most 1.2e-4 code in s, 5.6e-6 in pooled rms, 5.5e-5 in
  max cell. A fresh token-keyed fit replayed the same way shows the same size (`i4_fitcontrol.py`);
- **none moved.**

One untagged row (LT → edge-swap light-inactive) had run on `07b45391`, not `5ba68aeb`, and reproduces there.

**Readers: one output was contaminated.** `proof3_readers_b.replica.json` (`9c1623b4`):
- Its token-key replay (that commit's code, only the key changed) differs on the light checkerboard-8 / -64 λ
  rows over rrect-md / ml, by up to 10.4 codes: a capture rms of 11.18 reads 0.77, and gap bins flip between
  identifiable and non-identifiable. It also differs on two 1x checkerboard rrect-ml depth rows (0.85–0.87).
- An audit run of the same section with the ORIGINAL id key and a per-hit source check logged 15 hits whose
  stored blur came from another checkerboard pitch (0.10–1.0 encoded, 25–255 codes), on the checkerboard-8,
  -32 and -64 cells over the capsule, rrect-md and rrect-ml. Nine more hits served the same impulse backdrop at
  a rounded width and differ by at most 2.5e-9. The audit has its own allocation pattern, so its set of hit
  cells overlaps the record's contaminated rows without equalling them.
- **Substituted:** the token-keyed file is now `proof3_readers_b.replica.json`; the contaminated one is kept
  as `i4_contaminated_proof3_readers_b.replica.json`.
- **Effect** (`resolution_rows_b.json` regenerated): the light per-cell λ replica reading goes from FAIL
  (14 pass / 1 miss) to PASS (15 / 0). The light hinge-gap goes from 0.320 max, 21 misses, to 0.230, 13, still
  FAIL. Nothing else in the resolution rows moves.
- **The other 39 reader files replayed clean** (`i4_replay.txt`, READERS; 40 files in all, each by its
  producing commit's code and pin):
  - EXACT: proof1_readers_b step, step_w, patch, patch_w, lambda (on `5ba68aeb`, the pin it ran on; on
    `07b45391` it has 70 rows, not 66), lambda_w and u1; proof3_readers_b lambda; proof3_readers_a's four
    `.replica` files and four `.mirror` files; proof1_readers_a's four `model` files, three of its four
    `mirror,band` files and light-inactive `impulse,band`.
  - Within the fit's own rounding: proof1_readers_b depth (2.1e-6); proof3_readers_b step (calls identical,
    2e-5 on every well-conditioned value), depth (1.7e-5), patch and patch_given (one flat dark 1x rrect-lg
    receded fit whose w is ill-conditioned moves sn / sw by 0.02 %; two support rankings swap between tied
    rms values; no gated or scored call changes); proof1_readers_a light-rest `mirror,band` (one interval bound,
    0.003).
  - Written by an EARLIER reader revision than the commit that holds them, so compared on the rows
    `summarize_a.py` cites (`i4_sections.py` → `i4_sections.txt`): proof3_readers_a's four `<ep>.json` (every
    cited field EXACT; their `mirror` field is replaced by the `.mirror` re-run when cited) and
    proof1_readers_a's four `all` files and light-rest `impulse,band` (esf, heavy, exclusion and the dark
    impulse sections EXACT; the model / mirror / band / light impulse sections are replaced by later re-runs
    that replay clean). The one cited section that differs, the two-sided linear control, never touches the
    shared store (the probe counts 0 blur and 0 maps calls in all four endpoints), so no key reached it; see
    the note below.
- **Proof 2, the other half of the evidence** (`i4_fitcontrol.py`): a fresh token-keyed fit of two committed
  rows (LT-2k → LT and W-tails → LT, dark receded, `5ba68aeb`) records ls_pooled, s_ls, s and both points bit
  for bit as committed, and its own replay differs from it by exactly the committed rows' replay difference
  (−5.8e-5 and +1.18e-4 in s). The sub-1e-3 differences are therefore the fit's evaluation history (the key
  rounds a width to 1e-4 device px, so a blur computed at one width serves every width within 5e-5 during a
  fit); the replay itself is history-free (a no-cache control on the 72 differing rows equals it exactly).
- The four box-floor rows of `proof2_nulls-2xonly.json` reproduce on B' at BOTH scales (17 cells), not 2x only;
  the file's name does not describe them.

**Note, not I-4 (reader revision; recorded, not substituted).** The linear-control rows of
`proof1_readers_a.<ep>.all.json` are not reproduced by the committed reader code: every row's fit moves on a
flat optimum (on the 1x pitch-8 capsule `model_lin` σw sat on its 60-pt bound where the committed code reads
11.3–11.8), and several `mirror_lin` / `mirror_enc` identification flags flip. The section never reads the blur store, so this is the file predating a reader revision, not the
key. Regenerating it would move one note in `resolution_rows_a` (the two-sided control's S, max over
identified reads, 0.0035 → 0.0020) and no verdict. The parent decides whether to regenerate.

**Consequence.** The README's and §5.194 §5's claim that "no output from the window it was live shows it" is
FALSE for the readers. The proof-2, null and floor rows are clean.

**For the parent to fold.** In §5.194 §5:
- "No output from the window it was live shows it" and "the worst cell of every such row is under 3" are both
  false. 30 pre-fix proof-2 rows have a worst cell of 3.0–12.8, and one reader output WAS contaminated.
- Replace them with the replay's result: proof 2 clean; `proof3_readers_b.replica` contaminated and replaced,
  which moves the light per-cell λ replica verdict to PASS and the light hinge-gap to 0.230.
- §5.194 §3's proof-3 sentence "the per-cell λ ... miss" holds in dark only.

## I-5 (minor): part D's decimated-blur check

**Changed.** `proof1_families.fresh()` gives the cell a new token (and clears its cache) before each direct
render, in both the interpolation check and the decimated-blur check.

**Re-run** (`e7b767da`):
- decimated wide blur against direct: 0.0366 max, 0.0075 rms over 383 cells, the value first recorded and now
  actually measured;
- narrow interpolation: 0.0938 max, 0.0248 rms.

## I-6 (minor): the nulls' bar and mask

**Changed.** `proof2_nulls.py` no longer forces the fallback mask. A null that misses its declared bar is
labelled "NOT REFUSED: non-identifiable by the declared pooled bar".

**Re-run** (`c5d246e9`): all 20 nulls at the narrow mask, pin `764217e1`.

| null | pooled rms | bar | verdict | worst cell (descriptive) |
| --- | --- | --- | --- | --- |
| texel | 1.71–2.61 | 4.65 | NOT REFUSED | 9.8–12.7 |
| device px | 1.17–1.41 | 4.65 | NOT REFUSED | 8.5–10.1 |
| R2 | 1.71–2.84 | 4.65 | NOT REFUSED | 4.2–9.4 |
| mixture, light active | 2.56 | 2.60 | NOT REFUSED (new: the review-era row read 2.68, at an older pin with 42 cells) | 9.3 |
| mixture, elsewhere | 2.78–4.13 | 2.60 | PASS | — |
| box floor | 0.99 / 1.27 active, 0.41 / 0.43 receded | none | — | 6.1 / 8.9 active |

**Record.** These nulls are non-identifiable by the declared bar on this bed's synthetic proof. The 1x pass
referees the unit in the sitting.

**For the parent to fold.** In §5.194 §3 and §6 and in `declaration.md` `rejectedNulls`:
- "refused on its worst cells" becomes "not refused by the declared bar; non-identifiable";
- add the light-active mixture;
- add all of them to `nonIdentifiable`.

## I-7 (minor): masks in the bookkeeping

**Changed** (`04c1ada5`, `6d824e98`):
- `report_readers_b.py` cites the narrow-support rows for the gated step call (7 active D cells per endpoint,
  no call) and for the active patch σw and λ / hinge-gap rows. The W-support rows are cited as the fallback's
  record.
- `resolution_rows_b.json` is regenerated.
- The comments in `forward.py` and `proof_common.py` are corrected.

**Changed readings.**
- The active patch σw reads 5.0 % at the narrow mask (PASS). The fallback read 7.1 % (FAIL).
- The per-cell λ reads 30/33 identified light cells and 11/33 dark (was 17/20 and 5/20).

## I-8 (minor): minimax convergence

**Changed.** The comment now states the real drops (up to 1.26–1.68 codes). `proof2_minimax_check.py`
continues each row from its recorded minimax point with 120 + 60 Nelder-Mead evaluations, three times the
separation budget.

**Re-run** (`2da1c69e`): every row with three or more dimensions and s in [1.0, 2.1].

| row | recorded s | best s | converged | verdict |
| --- | --- | --- | --- | --- |
| K2 → W-tails light (whole) | 1.619 | 1.597 | yes | DISTINGUISHED |
| K2 → W-tails dark (whole) | 2.060 | 2.056 | yes | DISTINGUISHED |
| K2 → W-shape dark | 1.680 | 1.678 | yes | DISTINGUISHED |
| W-tails → K2 light | 1.810 | 1.810 | yes | DISTINGUISHED |
| LT → LT+bleed-own light (whole) | 1.279 | 1.279 | yes | MARGINAL |

No verdict changes. LT → free-sn light (2.22, seven dimensions) is outside the window and was not re-searched.

## I-9 (minor): README statements

- **Line 19:** only the rows of parts An, Aw, An_final, Aw_final, A_fix and E, and the separation, null and
  refraction-order rows, carry a pin. Parts A, B and C ran on `5ba68aeb` without one.
- **Line 126:** the bed does NOT separate endpoint k values 0.05 apart. The per-scheme level's light pair
  (Δ 0.052) reads 0.43, UNRESOLVED, and Δ ≈ 0.07 reads 1.23, MARGINAL.

**For the parent to fold.** `declaration.md` `kNesting` carries the same false sentence ("the bed separates
endpoint k values more than about 0.05 apart").

## I-10 (minor): proof-1 starts off their truths

**Changed** (`proof_common.starts_for`):

| parameter | start | truth |
| --- | --- | --- |
| W-tails s2 | 28 | 40 |
| W-tails a | 0.15 | 0.25 |
| k_b | 1.6 (alternative start 2.5) | 2.0 |
| free-sn receded ordinates | 3.5 / 4.2 / 4.8 / 5.8 / 6.8 | 4.25 / 4.8 / 5.4 / 6.5 / 7.5 |

**Re-run (part A_fix).** Every recovery stands:
- W-tails: s2 within 0.47 pt, a within 0.005, in all four endpoints;
- LT+bleed-own: k_b within 0.004;
- free-sn receded: every ordinate within 0.007 pt, including 128 and 160.
