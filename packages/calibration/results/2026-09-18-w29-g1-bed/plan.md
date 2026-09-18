# The 27 bed's eight passes — re-priced off the committed 27 keys

W29 G1 (5). G0 priced the passes before the 27 profile keys existed, from the 26.5 declaration
(`results/2026-09-18-w29-g0-preflight/plan.md`). `price-passes.py` beside this file re-derives the
table from the **27 keys `scenes.json` version 6 now declares**, so the plan and the file a pass
actually reads cannot disagree. The seconds per cell are G0's measurement on 27 and are not
re-measured: **10.09 s/cell** (`timing.py`, 22 attested scratch runs; 26.5 read 9.5 s, so 27 costs
about 6 % more), with launch, window presentation and manifest write together under half a second,
which is why a pass is priced on cells and not on runs.

## The eight passes, at the seven-run bar

A **pass** is one scale, one accessibility mode and one pose — the unit `run-sitting-27.sh` takes,
because the accessibility mode is a read-only system value set in System Settings and the pose is a
launch-time property of the process. A **cell** is one profile × one scene: the `--scenes` id count
is what the command line carries and the cell count is what the machine spends, and for the standard
passes they differ because the light and dark profiles declare overlapping lists.

| pass (scale × a11y × pose) | profiles | `--scenes` ids | declared cells | 26.5 published | one run | seven runs | with 1.3–2.5× attempt loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2x × standard × active | 2 | 96 | 162 | 161 | 27.2 min | 3.18 h | 4.13–7.95 h |
| 2x × standard × inactive | 2 | 72 | 119 | 117 | 20.0 min | 2.34 h | 3.04–5.84 h |
| 1x × standard × active | 2 | 96 | 162 | 162 | 27.2 min | 3.18 h | 4.13–7.95 h |
| 1x × standard × inactive | 2 | 72 | 119 | 117 | 20.0 min | 2.34 h | 3.04–5.84 h |
| 1x × increased-contrast × active | 1 | 10 | 10 | 10 | 1.7 min | 0.20 h | 0.26–0.49 h |
| 1x × increased-contrast × inactive | 1 | 22 | 22 | 22 | 3.7 min | 0.43 h | 0.56–1.08 h |
| 1x × reduced-transparency × active | 1 | 9 | 9 | 9 | 1.5 min | 0.18 h | 0.23–0.44 h |
| 1x × reduced-transparency × inactive | 1 | 21 | 21 | 21 | 3.5 min | 0.41 h | 0.54–1.03 h |

- **8 passes, 624 declared cells**, of which **619** were ever published on 26.5.
- one round over every pass: **105.0 min**
- seven runs: **12.25 h** (G0 published 12.24 h from the 26.5 declaration; the difference is
  rounding, and the cell counts are identical pass for pass)
- with the W27 record's 1.3–2.5× attempt loss: **15.9–30.6 h**

These are hours of **machine unavailability**, not of work: the idle gate means the machine must be
untouched, and contract X7 forbids a browser suite beside it. The bed costs days of machine
unavailability rather than hours of work.

## The order to run them in

**Standard first, both scales, both poses** — four passes, **11.03 h** at the bar, 14.3–27.6 h with
attempt loss. They are the four profiles every fidelity claim is fitted on and they need no hand on
System Settings; the two 1x passes need the BetterDisplay screen at displayplacer mode 69 and back
to 68 afterwards, which `run-sitting-27.sh` refuses on rather than discovering afterwards.

**Then the four accessibility passes** — **1.22 h** at the bar, 1.6–3.0 h with loss. Each needs the
user's hand in System Settings › Accessibility › Display, and both the script and the harness refuse
a pass whose declared mode the machine is not in, so a wrong toggle costs the pass rather than
mislabelling a fixture. On 26.5 macOS force-coupled Reduce Transparency on with Increase Contrast;
whether 27 still does is read from the machine per run and recorded, never assumed.

## The five cells declared on 27 that 26.5 never published

All five are on a dark-standard profile, and G0 named them so G2 does not meet them as absences in a
diff:

```
1x-dark-standard/light-solid__capsule-button__inactive
1x-dark-standard/photo__glass-over-glass__inactive
2x-dark-standard/checkerboard-8__capsule-button__rest
2x-dark-standard/light-solid__capsule-button__inactive
2x-dark-standard/photo__glass-over-glass__inactive
```

The first of those — `light-solid__capsule-button__inactive` on both dark profiles — is the scene
claims §5.148 §1 already found the publishing run passing over with no committed native fixture. A 27
pass attempts all five; whether any of them files is a finding for `sitting.md`, and a 27 cell with
no 26.5 counterpart is a cell G2 reports rather than diffs.

## What the rehearsal proved, and what it could not

`rehearse-all.sh` runs the four standard passes under `DRY=1`: every cell presented and attested
through the real bundle, the real declaration and the real machine state, nothing captured. It prints one line per
**cell**, so its counts are the declared-cell column above — 162 active and 119 inactive at each
scale — and not the `--scenes` id counts, which are smaller for the standard passes because the light
and dark profiles declare overlapping lists. The count is the verdict rather than the exit status,
because the script treats any nonzero count as success.
All four ran clean on 2026-09-18 (`logs/rehearsal.txt`, and the four `attest.read` / `attest.close` pairs
under `attest/`):

| pass | cells presented | wall clock | s/cell |
| --- | ---: | ---: | ---: |
| standard × inactive × 2x | 119 | 13 m 03 s | 6.58 |
| standard × active × 2x | 162 | 17 m 44 s | 6.57 |
| standard × inactive × 1x | 119 | 13 m 01 s | 6.56 |
| standard × active × 1x | 162 | 17 m 42 s | 6.56 |

Every count is the declared-cell figure above; no `WOULD REFUSE` and no `error:` line was printed;
no cell was filed under a 26.5 key; the pose attestation is uniform within each pass; and the closing
attestation read is identical to the opening one on all four. The rehearsal cost **1 h 02 m** of
machine time including the two display switches — a real line in the sitting's budget rather than
free. At 6.57 s/cell it reproduces the W27 sitting's dry rate, and the difference from the real
10.09 s/cell is the settle loop and the capture that a dry cell skips.

The two accessibility modes are **not** rehearsed from this session: each needs a hand in System
Settings, and a rehearsal without that hand would only exercise the refusal.
`run-sitting-27.test.sh` exercises it against a stubbed machine, and the real rehearsal belongs
beside the real pass — the runbook puts it there.
