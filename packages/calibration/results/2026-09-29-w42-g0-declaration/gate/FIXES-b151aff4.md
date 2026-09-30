# W42 G0 gate stream: fixes for the review of b151aff4

Branch `w42-g0-fix-gate`, off `w42-g0-declaration` at 9a695ec0. This file is for the parent to
fold into the declaration, the charter and ledger §5.194; none of those files, `declaration.json`,
`declaration.md` or `declare.py` was touched. One entry per finding in the dispositions (sections
"Gate review" and "Declaration assembler's open items", A1). Paths are relative to
`packages/calibration/results/2026-09-29-w42-g0-declaration/gate/` unless they start with
`packages/`.

## G1 (major, FIX): an unstaged gated WebGPU pair, and the broken kept-pair flag

- `owner/run-owner.py`:
  - `_union` no longer counts carried holdout rows as kept. `keptRowsByPair` and
    `keptRelocatedByPair` are built only from pairs no stage replaces, so
    `keptWebgpuPairsOfGatedProfiles` now names only truly kept pairs. Before the fix it named
    all six profiles in every rehearsal summary.
  - New refusal (exit 2), checked for both runs before either executes: a run whose documents
    replace one that a gated profile's WebGPU rows were drawn at, and whose stages do not render
    that pair. It uses `GATED_PROFILES`, clause 10's six, and `unstaged_gated_pairs`.
- `owner/proof-inputs.py`: the light stages now hold all four light gated profiles' WebGPU rows
  (1x and 2x standard, reduced transparency, increased contrast): 282 rows, 386 captures.
  `{base,cand}-light-no-rt/` is the synthetic stage that omits reduced transparency.
- Red/green proof (`owner/proof.txt`, "The fix wave"):
  - `g1-red-no-rt` omits reduced transparency's WebGPU pair and exits 2 with "candidate:
    apple-macos-27.0-1x-light-reduced-transparency-glass0.5 webgpu drew at a document this run
    replaces and no stage renders it".
  - `green` stages all six pairs and passes, with `keptWebgpuPairsOfGatedProfiles` [].
  - `g2-green` is the G2-shaped (holdout-carried) run and gives [] as well.
- `rehearsal/README.txt:154` is corrected beside the line. The rehearsal stages held only the
  four standard profiles; reduced transparency and increased contrast were kept at their old
  documents and gated nothing for either candidate.

## G2 (major, FIX): the seal's recording edits in the owner run

`owner/run-owner.py`, step 8, which extends the closure step of 9af438e3.

- **Logging.** Before each of the test's three named-miss assertions (`MISSED_27_ROWS`, L1
  `MISSES`, and the new L1 `GROWTH_MISSES`), the worktree copy logs four things, one added line
  per list, with no assertion changed:
  - the derived list;
  - the recorded list;
  - each derived entry's pinned readings, in the test's own scope: a table row's `reading`, an
    M1 miss's R, an M2 named miss's |Δ| and `native`, and an L1 growth miss's growth;
  - the recorded entries.
- **The seal's edits.** Then, as the seal would:
  - **Closures.** A recorded entry that is no longer derived is dropped. Its `MISSED_27_ROWS` or
    `GROWTH_MISSES` line is deleted, and a `MISSES` member is filtered at its assertion.
  - **Re-records.** A recorded entry that is still derived, but whose reading no longer pins
    (|Δ| ≥ 5e-6, `toBeCloseTo(…, 5)`), gets that field rewritten in its own line. A field the
    entry lacks is never added.
  - **Nothing is added.** Additions come only through step 6's two named paths: M2 (Decision Log
    5a) and L1 growth (A1). An entry that is derived but not recorded still fails.
- **Second run.** The test runs again, and that run is the result. If it still shows a closure
  or an unpinned reading, the runner stops.
- **Logging and reporting.** Every edit is logged in `<run>/edits.txt`, including the named-path
  insertions (`m2-insertions.txt` and `l1-growth-insertions.txt` stay). `summary.json` reports
  `closures` as a list of its own per run, plus `reRecorded` and `edits`.
- `CLOSURE_ASSERTIONS` keeps its 3-tuple shape, which `declare.py` unpacks, and gains the
  `"L1 GROWTH_MISSES"` anchor. The readings live in a separate `CLOSURE_READINGS`.
- `owner/README.txt` (steps 6, 7a and 8) states all of this.
- Proof (`owner/proof.txt`): `closure-move` closes two named misses (the `MISSED_27_ROWS` 1x
  rrect-sm inactive R entry and the L1 `MISSES` 1x tinted impulse capsule). It also moves the
  other two M1 misses, which still miss: 1.46115 → 1.43 and 1.4495 → 1.42. The first vitest run
  fails 2 cases. After the seal's edits (2 closures, 2 re-records; `edits.txt`) the second run
  passes 109/109, exit 0. `closure-move-no-closures` fails 2 new cases, exit 1.
  `closure-move-plus-new` still blocks (3 new failures, exit 1), because the edits never add an
  entry. `m2-toward` (M2's named path) still passes with its one insertion.

## G3 (major, FIX, record)

`rehearsal/round3/README.txt`:
- M2 joins the `[SEAM]` list, and the Key marks active-pose named moves as seam-driven.
- The round-1 active-pose "named" readings (`rehearsal/README.txt` light active and dark active
  M2) are annotated as seam-driven, with the reviewer's dark-capsule example, checked against
  `runs/c1|c2/owner-summary.json`: +2.14 / +4.28 % under C1 and +5.56 / +10.35 % under C2, all
  named.
- I checked that Apple's `interiorStdDevNative` exceeds vitrea's on all 26 M2 bed cells, at 1.25
  to 4.6 times.
- The note that M2 on this bed fails only on flattening, and that Stop P and the eye sheets
  catch wrong added texture, is in the `[SEAM]` entry.
- **For the parent:** record the flattening-only reading in §5.194 and tell the user.

## G4 (major, DISMISS as overtaken by Decision Log 5e)

- No reading was run.
- `rehearsal/round3/README.txt` notes, beside its E2 conclusion, that the adopted reading was
  never run on c1f/c2f, and that the cause it names is attested only where the shells are held.
- `README.txt` (gate) records the dismissal.

## G5 (minor, FIX, label)

- `rehearsal/round3/README.txt` labels `[U7]` and `[P1]` as read through the active swap's
  unmeasured error. The active pose has no control; the replica misses by 1.59–2.07 codes rms on
  2x checkerboard-8 rrect-lg, above the swap's 1-code drop threshold. G2's real renders decide
  both.
- The reviewer's "+0.0051 / +0.0055" is not a round-3 reading (r3-2pgb's [U7] is checkerboard
  rrect-ml +0.0105), so the label cites round 3's own figures.

## G6 (minor, FIX)

- The reviewer's two seeds were added to the owner case in
  `packages/calibration/test/adopted-thresholds.test.ts`:
  - "past a flatter Apple by 5 %" → failure;
  - "past a far more textured Apple by 1.5 % of it" → named.
- `m2-named-miss/mutants.py` / `mutants.txt` show the effect:
  - At 9a695ec0, both mutants of `structureVerdict` (the `Math.abs` dropped, and dividing by r)
    pass all 107 cases.
  - With the seeds, the owner case fails on each mutant, on the matching seed.
  - The unmutated file passes 108 cases with 1 skipped.

## G7 (minor, RECORD, no change)

- `README.txt` (gate) records the /n reading with the reviewer's example: r 0.0200, n 0.0201,
  w 0.0205 is named, at 1.99 % past n.
- /n is the lenient choice wherever n > r, which holds on every bed cell.
- **For the parent:** record the reading beside Decision Log 5a in the charter and §5.194.
- G6's seeds now pin /n and the absolute distance exactly as implemented.

## G8 (minor, FIX)

- `owner/run-owner.py` reads the bar only against a base that passes every case.
- A base with any failure refuses (exit 2) after `summary.json` is written (`refused`, plus the
  verdict for evidence). The reason: vitest truncates the messages a shared failure is compared
  on.
- Proof `g8-red-shared` seeds the same L1 miss in base and candidate: exit 2. Both runs fail 3 cases, and the verdict records all 3 as
  shared. The old
  proof's `red-shared` read the same seed as shared, exit 0.

## G9 (minor, FIX)

Changes in `stops/`:
- **Declaration.** `stops-declaration.json` is now v2, with a dated revision entry.
- **The new statistic.** `halo.py` adds `floor`, the median of the floor ring (8 ≤ r < 10)
  in absolute encoded codes. It uses the same bar, and a cell passes only if all three
  statistics pass.
- **Output.** `stops.py` text output includes the floor.

Proof results (`stops/proof.txt`, 38 of 38 pass):
- **Synthetic case.** A σ-20 halo against a narrow Apple and an over-strong narrow shipped halo
  passes peak and annulus but fails floor (147 against 120), on both shapes at both scales.
- **End to end.** Moving the whole r < 10 disc 3 codes away from Apple's floor fails floor on
  all 16 cells; peak and annulus are unchanged.

Baseline (`stops/baseline.txt`), floor medians, Apple against shipped:

| Endpoint | Apple | Shipped |
|---|---|---|
| Light active | 133.5 | 132.0 |
| Light receded | 134.0 | 138.5 |
| Dark active | 33 | 54 |
| Dark receded | 23 | 30.5 |

The tight cell is light 2x capsule rest (dShip 1.0).

**Beyond the brief: the round-3 swap trees re-read.** The 24 round-3 swap trees were re-read by
Stop H with the floor (`rehearsal/round3/stopH-floor.txt`, entry `[HF]` in round 3's list):
- **Candidate 2.** Every blended combination, r3-2pgb included, gains one Stop H failure: the 1x
  light active tinted impulse capsule's floor reads 132.11 against Apple's 127.69 and shipped's
  130.97, 0.14 code past the allowance. This is a near-bound reading inside the active swap's
  unmeasured error, like [P1].
- **Candidate 1.** The dark receded capsule floor reads 4 against Apple's 23, which is the landed
  T's per-pixel black end.
- **For the parent:** this changes what "light active under 2pgb fails only [U7] and a marginal
  [P1]" says, and the user may need to hear it.

**Limit.** The floor is absolute, so it also moves with the body's own level beside the dot. This
is recorded in the declaration's limits.

## G10 (minor, FIX)

Changes in `stops/stops_common.py` and `stops.py`:
- **Declaration required.** Every non-shipped document a candidate names must be declared with
  `--document`, even when no `--document` is given.
- **Shipped candidates refused.** A run where every scheme names the shipped documents is
  refused. So is the shipped tree given as the candidate root.
- **`--baseline`.** This is the one run that reads the shipped tree against itself. The candidate
  root must equal the shipped root, and the run is stamped "baseline".

Proof results (`stops/proof.txt`, E1 and E4):
- **Refusals.** The shipped tree is refused as a candidate, and an undeclared scratch document is
  refused when no `--document` is given.
- **Identity.** The shipped captures, renamed to four declared scratch documents, read
  dCand − dShip = 0 on all 100 statistics.

The baseline was regenerated with `--baseline`.

## G11 (minor, FIX)

- **The change.** `referees/chroma-cut.py`, in candidate mode, writes each admitted candidate into
  `shippedDocuments` in place of the `profiles/` file with the same basename (`measured_documents`).
- **Base mode is unchanged**, and the admission test shows it is still byte-identical to W41's
  port.
- **The check.** `referees/test_admission.py` now checks, before mapping, that the candidate cut
  names the four candidates.
- **The run.** `referees/admission-test.txt` was re-run: 75 ok, 0 FAIL.

## A1 (FIX, the parent's design call): L1 growth's named-miss path

**The test.** `packages/calibration/test/adopted-thresholds.test.ts` adds, beside L1's `MISSES`:
- `GROWTH_RULED`, Decision Log 5d's four cell-profiles: light
  `photo__rrect-md__inactive-tint-orange` and dark `photo__capsule-button__inactive-tint-orange`,
  each at 1x and 2x.
- `growthVerdict`: a growth miss (> 0.005) on a ruled cell is named; anywhere else it is a
  failure.
- `GROWTH_MISSES`, which is EMPTY today.
- **The growth case.** It is retitled "… or is a named growth miss (W42 Decision Log 5d)". It
  excuses only a named miss that is recorded, and a failure fails even when listed.
- **The owner case.** It seeds every arm of `growthVerdict` and holds the ruled set inside the
  population. It holds the named set equal to the recorded set in both directions, each growth
  to five decimals, and allows no growth failure.
- The 0.005 bound and the absolute clause are unchanged.

**Live suite: 108 passed, 1 skipped (X1).**

**Red/green** (`l1-growth-named-miss/red-scenarios.py`, `red-green.txt`), eight scenarios on
throwaway copies:

| Case | Result |
|---|---|
| Ruled cell unlisted | red |
| Ruled cell listed | green |
| Stale reading listed | red |
| Closed entry listed | red |
| Unruled cell, unlisted | red |
| Unruled cell, listed | red |
| Four ruled cells listed at r3-2pgb's growths | green |
| Four ruled cells plus a fifth | red |

**The runner** (`owner/run-owner.py`):
- It inserts every growth miss on a ruled cell from the regenerated L1 cut into `GROWTH_MISSES`,
  as the seal would, but only where the test carries the path. The test checks each insertion.
- It inserts nothing else, so a fifth growth miss blocks.
- The switch `--no-l1-growth-named-misses` turns this off, for evidence.

**Proof** (`owner/proof.txt`): all at 44462152, with 109 cases (A1's owner case included).
  - `a1-green` stages the four ruled cells at r3-2pgb's growths. Four entries are inserted
    (`l1-growth-insertions.txt`): measured 0.0108, 0.0100, 0.0138 and 0.0133. The candidate
    passes 109/109, exit 0.
  - `a1-fifth` adds 1x light checkerboard__rrect-ml__rest at +0.0105 (round 3's [U7] reading).
    It is not inserted, and it fails 2 new cases: the growth case ("a failure, which no entry
    excuses") and the owner case. Exit 1.
  - `a1-no-insertion` runs a1 with `--no-l1-growth-named-misses`. The four ruled misses read as
    2 new failures. Exit 1.

**For the parent:**
- The declaration item `l1TintedReceded.declared.ownerTest` (it says the committed owner test
  has no named list for L1 growth) is now stale.
- Clause 12's exception now covers two derivations. The parent's call extended it; the charter
  should say so.

## Other checks, and what the parent re-pins

- Calibration suite and lint: run at the branch head, on a machine at load 100 to 245 (other
  processes).
  - `adopted-thresholds.test.ts`: 108 passed, 1 skipped (X1, no capture tree in a worktree).
  - `pnpm run lint` (eslint and the four tsc projects): exit 0.
  - The calibration suite (`vitest run`, 60 files): 775 passed, 1 skipped, 2 failed. Both
    failures are timeouts, in files this wave does not touch, and both pass when given time:
    - `matrix-write-guard.test.ts` ("diff refuses canonical matrix and report destinations
      before measurement") hit its 5 s case timeout, twice. It passes 5/5 with
      `--testTimeout=120000`.
    - `w41-instrument.test.ts` (exposure/test_runner.py) hit its 90 s spawn timeout, twice. Run
      directly, `test_runner.py` passes 41 tests OK in 151 s at load about 245.
- `freeze.py verify`: 1,818 entries.
- `declare.py check` at the branch head: every derived check passes, and the only mismatches
  are SHA-256 pins of files this wave changed. These need re-pinning:
  - `gate/owner/proof-inputs.py`
  - `gate/owner/proof.txt`
  - `gate/owner/run-owner.py`
  - `gate/referees/admission-test.txt`
  - `gate/referees/chroma-cut.py`
  - `gate/rehearsal/README.txt`
  - `gate/rehearsal/round3/README.txt`
  - `gate/stops/baseline.txt`
  - `gate/stops/proof.txt`
  - `gate/stops/stops-declaration.json`
  - `gate/stops/stops.py`
  - `packages/calibration/test/adopted-thresholds.test.ts`

  Other files changed or added here are not pinned today. They are listed in case the parent
  wants them pinned:
  - changed: `stops/halo.py`, `stops/stops_common.py`, `stops/proof.py`, `stops/README.txt`,
    `referees/test_admission.py`, `referees/README.txt`, `owner/README.txt`, `README.txt`;
  - new: `owner/run-fixgate.sh`, `l1-growth-named-miss/*`, `m2-named-miss/mutants.*`,
    `rehearsal/round3/stopH-floor.txt`.

## Commits

On `w42-g0-fix-gate`, oldest first; this file is added by the last commit.

- `c8137436` W42 G0 fix (gate A1): L1 growth gets Decision Log 5d's named-miss path
- `06f758af` W42 G0 fix (gate G6): two seeds pin M2's past-Apple clause
- `ee2205d8` W42 G0 fix (gate G9, G10): Stop H reads the floor; the stops refuse the shipped render
- `44462152` W42 G0 fix (gate G1, G2, G8, A1): the owner runner reads what the seal would
- `c44ed675` W42 G0 fix (gate G11): a candidate chroma cut names the documents it measured
- `c53986d9` W42 G0 fix (gate G1, G3, G4, G5, G7): the rehearsal's records say what they read
- `60242fd0` W42 G0 fix (gate G9): the round-3 trees re-read by Stop H with its floor
- `681d5f26` W42 G0 fix (gate G1, G2, G8, A1): the owner runner's proof and README
