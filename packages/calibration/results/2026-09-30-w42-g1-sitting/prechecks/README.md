# W42 G1 phase 1 — the pre-grant checks (c9a §5.195)

Charter: `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`, G1 and Decision Log 6.
Runbook: `../../2026-09-29-w42-g0-declaration/bed/sitting/README.md`. Worktree `w42-g1-sitting`
at `19db06ec`; `sitting.py pin-check` passed against the hashed declaration `f04ae95b…`
(scenes `4aa06af9…`, bed `53870f47…`); `freeze.py verify` reads 1,818. Raw captures and runs
stay under `~/vitrea-w42/g1/` (`prechecks/`, `rehearsal/`, `rehearsal-attempt-2/`) and are
never committed.

## Check 1 — the ORIGINAL bundle's positive capture: PASSED on its attestations (parent's ruling)

`original-positive.py original-positive-1` (W39 G1's `wave-close/grant-check-close.py` with the
W42 driver's gates). The original bundle `dev.vitrea.reference-apple` (binary `bd3092e8…`,
cdhash `88cbbb5b…`, the same binary W39 closed on, not rebuilt) captured the canonical 27-only
2x light checkerboard capsule at mode 68. It waited 1 h 27 min without launching, until
Google Chrome and ChatGPT had been quit by the user, then for 75 s of HID idle
(`original-positive-1/wait.txt`; the script writes `<attempt>-wait.log`, renamed here because
`*.log` is gitignored, as is `backgrounds.txt`). It launched with zero foreign processes and
ChatGPT gone (`command.json`), and the opening and closing machine reads agree.

| Condition | Read |
| --- | --- |
| outcome | `captured-active` |
| `materialRendered`, `presentedActive`, `deterministic` | true, true, true |
| `repeatNoise` | 0 |
| byte-identical to the committed fixture (`6c15311b…`) | **no**: frame `204f21f0…`, 115 px differ, 114 by 1 code and 1 by 2, all inside the capsule body (x 200–440, y 155–254), slightly brighter |

The brief required byte identity, so the check stopped there and handed back before check 2
(commit `c224b7f0`).

**The frame is a known second state, not a drift** (`two-states.py` → `two-states.json`). It is
byte-identical to W39 G1's step-0 capture of the same bundle (`204f21f0…`, 2026-09-25), which
W39's README recorded as "115 pixels by ≤ 2 codes" and did not gate on. The committed fixture's
state `6c15311b…` is what W39's side pose check 2 and W39's close check produced. Every one of
the four stored checks attests active, material rendered, deterministic and repeat noise 0, so
the cell takes one of two states per launch, each stable within its launch.

**The parent's ruling (2026-09-30).** Check 1 PASSES on its attestations. For this unrebuilt
binary (`bd3092e8…` / `88cbbb5b…`) the restore baseline is **one of the two recorded states,
`204f21f0…` or `6c15311b…`**: the original's positive check at the sitting's end is compared
against both hashes, and matching either is a restore.

**G1 finding — a hypothesis, not established: the cursor window at launch.** Four captures,
two per state, split exactly by whether a Window Server window at level 2147483630
(kCGCursorWindowLevel) was on screen when the launch began. Both `204f21f0` launches (W39 step 0,
this check) began without it, and it appeared during the launch; both `6c15311b` launches (W39
side pose check 2, W39 close) began with it present. Four observations cannot separate this
from any other launch-level condition that happened to co-vary, so it is recorded as a
hypothesis. Nothing is gated on it; the restore check accepts either state.

## Machine state after check 1

Display mode 68 on `7709FD0F-…`, never changed. Reduce Transparency 0, Increase Contrast 0,
`NSGlassTintAmount` 0.5, Show Borders 0. The system TCC rows, read read-only before, after and
at the stop, were unchanged. `dev.vitrea.reference-apple` has Screen Recording auth 2
(2026-09-27 05:08:28Z) and Accessibility auth 2. `dev.vitrea.reference-apple.w39` has **no
row**, and the only other row is `dev.vitrea.tccprobe` at 0. No harness process remained, and no
permission prompt was on screen during check 1.

## Check 2 — the TCC-refusal rehearsal of the ungranted side bundle: PASSED at attempt 2

The runbook's command, through the orchestrator's display trap:
`REHEARSAL=1 PASSES="2x-light-active 2x-light-receded 1x-light-active 1x-light-receded"`, the
side bundle `~/vitrea-w39/side/VitreaReference.app` (`dev.vitrea.reference-apple.w39`, cdhash
`be258cbf…`, binary `02052b17…`, the W39 pin), real run-1 argv. `rehearsal/collect.sh <root>
<attempt>` copied each attempt here through the sitting's `collect-pass.py`, adding each run's
idle log as `driver-idle.txt` (`*.log` is gitignored), the harness's stderr and the orchestrator's
logs. `runs.json` reads `admitted: false` for every rehearsal run by construction: a rehearsal
writes `rehearsal.json`, never an admission.

**Attempt 1 (`rehearsal/attempt-1/`, root `~/vitrea-w42/g1/rehearsal`): prompt-pending, stopped.**
The side bundle had no TCC row. Its first launch (2x-light-active) attempted the capture and
printed the TCC-gate sentence, but a `universalAccessAuthWarn` window appeared during it, so the
driver quarantined the run `prompt-pending` and the orchestrator stopped, restoring and verifying
mode 68 (10:06:48Z). The other three passes did not run. **The prompt wrote the TCC row itself**:
`.w39` ScreenCapture auth 0 at 10:06:47Z, read while the prompt was still up and unanswered,
contrary to W39 G0's note that a pending prompt writes none (`attempt-1/prompt.txt`, with the
prompt's text and buttons read by osascript). Nothing clicked Allow. The parent clicked 거부
(Deny) through cua_repl; the row stayed auth 0.

**Attempt 2 (`rehearsal/attempt-2/`, fresh root `~/vitrea-w42/g1/rehearsal-attempt-2`): all four
`refused-tcc`, no prompt.** 10:36:22–10:37:17Z; the switch to mode 69 waited on 300 s of idle
(`logs/mode-switch-idle.txt`) and the trap restored mode 68, verified.

| Pass | Mode (open / close) | Outcome | Capture attempted | TCC-gate sentence | Manifest / PNG / staging / new window / timeout |
| --- | --- | --- | --- | --- | --- |
| 2x-light-active | 68 / 68 | refused-tcc | yes | yes | none |
| 2x-light-receded | 68 / 68 | refused-tcc | yes | yes | none |
| 1x-light-active | 69 / 69 | refused-tcc | yes | yes | none |
| 1x-light-receded | 69 / 69 | refused-tcc | yes | yes | none |

Every opening read: 27.0 / 26A428, tint 0.5, Reduce Transparency, Increase Contrast and Show
Borders 0, the side pin, 0 foreign processes, no prompt, ≥ 1,350 s of HID idle; every closing
read agreed. The TCC rows before and after (`attempt-2/before-attempt.json`,
`attempt-2/tcc-at-collect.json`) are identical: the recorded denial suppresses the prompt, as in
W39 G1's attempt 2.

A window `ChatGPT Computer Use|0` (owner `SkyComputerUseService`, Codex Computer Use.app, the
cua_repl helper, started 10:34:16Z) was on screen through attempt 2. The census does not name it
and a refusal cannot be affected by it, but a layer-0 window of another app is the kind that took
the active pose in W39 G1's stop 1; it is recorded for the sitting's active passes.

## State at the close of phase 1

Display mode 68 on `7709FD0F-…`, verified. X6 as above. System TCC rows (read-only):
`dev.vitrea.reference-apple` ScreenCapture auth 2 (2026-09-27 05:08:28Z) and Accessibility auth 2;
`dev.vitrea.reference-apple.w39` ScreenCapture **auth 0** (2026-09-30 10:06:47Z);
`dev.vitrea.tccprobe` auth 0. No harness process running, no prompt on screen. Phase 2 begins
with the grant switch, which is the parent's.
