# W42 G1 — the native sitting (c9a §5.195)

This is the sitting's operational index. The charter is
`docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md` (G1, Decision Log 6), and the
runbook is `../2026-09-29-w42-g0-declaration/bed/sitting/README.md`. Raw runs live under
`~/vitrea-w42/g1/run/` on the capture machine and are never committed. After each pass the
orchestrator copies that pass's attestations into `attest/<pass>/` and commits them.

- **Phase 1, the pre-grant checks** (`prechecks/README.md`): the original bundle's positive
  check passed on its attestations (the parent's ruling), and the side bundle's TCC-refusal
  rehearsal passed at attempt 2.
- **Phase 2, the grant switch and the side's pose check** (`grant/README.md`): the side bundle
  was `captured-active` at its first pose check. The original has no ScreenCapture row and is
  not launched.

## The sitting

Command: `VITREA_SITTING_DIR=~/vitrea-w42/g1/run W42_EVIDENCE=<this directory>
W42_EVIDENCE_REPO=<the G1 worktree> bash sitting-orchestrate.sh`, run detached.

### Start and stop 1 (2026-09-30 10:47:52Z – 10:59:58Z)

`dump-2x-light-active` was QUARANTINED, and the orchestrator stopped, restored mode 68 and
verified it (`attest/dump-2x-light-active/`, commit `bf5557bd`). `dump-layers` completed 87/87
scenes in 723.9 s. `dumpcheck` found 81 scenes on memo D's declared configuration exactly, and
**163 departures, all in the last six scenes in dump order**, dumped from 10:59:15Z on:
`h-g232-rrect-md`, `h-lc-c64-capsule-button`, `h-p1-c24-rrect-112`, `h-p3-c64-rrect-lg`,
`h-p6-c32-rrect-md` and `h-s24-hi-rrect-md`, all `__rest`. Each of those six reads
`isKeyWindow: false` and `appIsActive: false` and carries the unfocused-window material
(`hl.opacity` 0, `inputRefractionOpacity` 0, the shadow 0, `bd.marginWidth` 0.5). The dump had
launched key and active (`--require-key`), so **the window lost focus mid-dump, and no declared
constant departed**. The closing session read frontmost `com.apple.universalcontrol` and 44.2 s
of HID idle: input arrived at about 10:59:14Z, between the last good scene (10:59:07Z) and the
first bad one. A `WindowManager|18` window had also appeared. The Mac itself was untouched, so
the input came over Universal Control from the user's other device. The idle gate reads HID idle
only at a launch, and the census does not name Universal Control, so neither could see it.
Nothing was captured, and nothing was retried.

### Continuation 1 (the parent's explicit resume, 2026-09-30)

The parent authorised a resume as an explicit act, after these changes:
- the user switched Universal Control **off** on this Mac, so pointer and keyboard no longer
  cross over from the other device;
- Google Chrome, which the user had reopened, is closed, which the parent verified;
- Finder is frontmost, with no `WindowManager` window;
- the display is at mode 68;
- the TCC rows are unchanged: `.w39` is at auth 2, and the original has no ScreenCapture row.

The G1 worker read the same state before relaunching. The resume is the orchestrator's declared
continuation against the **same** run root and evidence variables:
`START_AT=dump-2x-light-active` (run 1, since `FIRST_RUN` is unset). The quarantine stays under
its own name, `dump-2x-light-active/QUARANTINE-run-1-1790765998327680000`, and the driver takes
a fresh `run-1` beside it. The idle gate waits out the user's recent touch, as designed.

### Stop 2 (continuation 1, 2026-09-30 11:13:09Z – 11:25:20Z)

`dump-2x-light-active` was QUARANTINED again (`QUARANTINE-run-1-1790767520002843000`, commit
`061f5601`), and the orchestrator restored mode 68 and verified it. `dump-layers` completed
87/87 scenes in 728.6 s. There were **317 departures, all in twelve contiguous scenes** in dump
order: `a-g192-rrect-md` through `a-g255-rrect-64`, the scenes written from 11:15:24Z to
11:16:57Z. Each reads `appIsActive: false` and `isKeyWindow: false` and carries the
unfocused-window material. The other 75 scenes, including stop 1's six, read memo D's
configuration exactly. The G1 worker's 20 s session trace (`~/vitrea-w42/g1/watch/`, raw)
shows the cause:

| Read at | Frontmost | HID idle (s) |
| --- | --- | --- |
| 11:15:14Z | `dev.vitrea.reference-apple.w39` | 205.1 |
| 11:15:34Z | `com.apple.universalcontrol` | 7.7 |
| 11:16:55Z | `com.apple.universalcontrol` | 88.1 |
| 11:17:15Z | `dev.vitrea.reference-apple.w39` | 108.2 |

Input arrived at about 11:15:26Z through the same `UniversalControl` process (pid 49435, alive
since 2026-09-29) with Universal Control reported off. No `WindowManager` window appeared this
time. The harness took focus back by itself at about 11:17:05Z. Nothing was captured, and
nothing was retried.

### Continuation 2 (the parent's explicit resume, 2026-09-30)

The user reports that Universal Control is now off, and asked for the sitting to run again. The
parent authorised the sitting's second continuation as an explicit act. Before the relaunch the
G1 worker read Finder frontmost, no Chrome, ChatGPT, cua helper, harness or orchestrator running,
display mode 68, and TCC unchanged (`.w39` auth 2, the original with no ScreenCapture row). The
`UniversalControl` process is still alive; that alone does not show the feature is on. The
command is again `START_AT=dump-2x-light-active` against the same run root and evidence
variables, with both quarantines kept under their own names. A 20 s session trace runs for the
whole sitting, not only the dumps, so any later loss of focus comes with its reads.

### Stop 3 (continuation 2, 2026-09-30 11:28:28Z – 15:23:25Z)

Continuation 2 admitted **every dump**: 8 of 8, 447 scenes, 0 departures. Each 2x active dump
has one `unpredicted` field, the rrect-112 SDF maximum, which is recorded and not a stop. It
then admitted **`2x-light-active` in full** (7 of 7 runs: run 1 has 133 cells, 87 glass and 46
references, and runs 2–7 have 87 each), and `2x-light-receded` runs 1–3 (148, 92, 92). The
session trace saw no HID input from 11:28:33Z on; only the harness or Finder was frontmost.

**`2x-light-receded` run 4 was QUARANTINED** (`2x-light-receded/QUARANTINE-run-4-1790781804771531000`,
commit `ff9ece16`) by the closing machine read: `machine gate refused: 11 foreign capture
process(es); X6 admits none`. The run opened at 15:08:45Z with 0 foreign processes and 13,313 s
of HID idle. All 92 captures, from 15:08:56 to 15:23:23Z, attest `presentedActive: false`,
observed pose `inactive`, material rendered and deterministic. At 15:23:05Z **another agent
session's `playwright-cli`** (a daemon, pid 8697, whose `npm exec` parent had exited) launched
Google Chrome with its helpers. Its `run-code` navigated to `tss.ucsd.edu`, which is not W42
work. The census counted them at the close. **No human input occurred**: HID idle stayed above
14,000 s, and nobody touched the Mac. The orchestrator restored mode 68 and verified it. Nothing
was retried, and the G1 worker killed no process belonging to another session.

### Continuation 3 (the parent's explicit resume, 2026-09-30)

By 15:24:47Z the parent had found no Google Chrome or Playwright process left, the last Chrome
crashpad handler having exited. The parent authorised the sitting's third continuation as an
explicit act, on the condition that the machine gate's own census reads zero first. The G1
worker ran `record-machine.py` and `sitting.validate_machine(…, 2)`. The census read 0 foreign
processes, and the gate passed: macOS 27.0 / 26A428, Reduce Transparency, Increase Contrast and
Show Borders 0, `NSGlassTintAmount` 0.5, mode 68, and the side pin `be258cbf…`. The session read
unlocked, with Finder frontmost and 14,316 s of HID idle. The command is
`START_AT=2x-light-receded FIRST_RUN=4` against the same run root and evidence variables. The
quarantine stays under its own name, and runs 1–3 stand as admitted. The parent has asked the
user to keep browser automation from every other session off this Mac until the sitting ends.

### Stop 4 (continuation 3, 2026-09-30 15:25:51Z – 15:25:53Z): the G1 worker's own error

The driver's opening machine read refused `2x-light-receded` run 4 before any launch:
`machine gate refused: 1 foreign capture process(es); X6 admits none`. The run is quarantined
as `2x-light-receded/QUARANTINE-run-4-1790781952880634000`, which holds only the opening reads
and the refusal (commit `18eb5935`). The one process was the G1 worker's own launching shell
(pid 18305, a child of the worker's session). The worker had put a guard, a `pgrep` over the
browser names, into the same shell command as the orchestrator call, followed by `sleep 2`, so
that shell's command line carried the census words while it waited. The census matches command
lines by name. It excludes only the reader's own ancestors, and the orchestrator detaches with
`setsid`, so the launching shell is not one of them and was counted. No harness launched,
nothing was captured, and the display stayed at mode 68, verified.

### Continuation 4 (the parent's explicit resume, 2026-09-30)

The parent authorised the fourth continuation as an explicit act, on the worker's fix. The census
and X6 check run in their own command, which exits before the launch. The launch command's line
holds only the orchestrator call, with none of the census words and nothing chained after it. For
the rest of the sitting, no command line of the G1 worker (or of the parent's other workers)
carries the census words, search patterns included. The command is again
`START_AT=2x-light-receded FIRST_RUN=4` against the same run root. Both run-4 quarantines stay
under their own names.

### Stop 5 (continuation 4, 2026-09-30 15:27:41Z – 16:11:42Z)

Continuation 4 admitted `2x-light-receded` runs 4, 5 and 6, with 92 cells each, so runs 1–6 of
that pass are now admitted. Run 7 was refused at its opening machine read at 16:11:41Z, before
any launch, with idle at 17,089 s and no human input: `machine gate refused: 1 foreign capture
process(es); X6 admits none`. It is quarantined as
`2x-light-receded/QUARANTINE-run-7-1790784701958598000`, which holds only the opening reads and the
refusal (commit `ae060b7e`).

The counted process was a W39 test stub's fake launch (pid 40834): a temporary `launcher.py`
whose arguments name a stub harness bundle under `/private/tmp/w39-test-side/`, so its command
line carries the harness's own name, which is a census word. The process chain was:
`test-archive.py` (37311) ← a vitest worker (36297) ← `vitest run` in
`~/vitrea-w42/g2-impl/packages/calibration` (30648) ← `npm exec vitest run` (30554, started
16:07:58Z) ← a shell of the parent's own session. One of the parent's G2 implementation workers
was running the calibration unit suite, whose Python sitting and archive tests spawn such stubs.
A rule about typed command lines cannot cover processes a test suite spawns. The parent ended
that test run at 16:13Z (30554, 30648, 36297, 37311). It barred both implementation workers
from the whole calibration suite, and from every Python test under `results/`, until the sitting
ends.

### Continuation 5 (the parent's explicit resume, 2026-09-30)

The parent authorised the fifth continuation as an explicit act, the same way as the fourth. The
census and X6 check run in their own command, which exits first; the launch line holds only the
orchestrator call. The command is `START_AT=2x-light-receded FIRST_RUN=7` against the same run
root, and the run-7 quarantine stays under its own name.

**The first pre-check refused, and nothing was launched.** The census, run as its own command,
counted one process: a `compare.ts` run with `--skip-capture` (pid 50021, already exited when
read). Its parent was a vitest worker (46765) of a **second** `vitest run` in
`~/vitrea-w42/g2-impl/packages/calibration` (46735 ← `npm exec vitest run` 46695, started
16:13:19Z), from a shell of the parent's session, seconds after the first run was ended. The
parent ended that run at 16:14:44Z. At 16:15:01Z it ended every orphaned vitest worker left under
`~/vitrea-w42/g2-impl`, pids 31027 to 52858: reparented to launchd, they were still spawning
test processes. Its scan at 16:15:01Z found no vitest, `compare.ts`, launcher or archive-test
process, and both implementation workers now hold the ban. The census is then rerun as its own
command, and the launch follows only on a clean read.

**The second pre-check read clean.** The census counted 0 foreign processes and the 2x gate
passed. Its scan also showed a third, short `vitest run` of named files in the G2 worktree
(`dark-profile-export`, `digest-supersessions`, `macos27-profile-export`, …), which spawns no
census-matching process and had finished seconds later. The census was rerun as its own
command: 0 foreign, no vitest process, the gate passed. The launch followed at 16:16:17Z. The
parent kept the ban as ruled: named-file runs are allowed, since none of their processes can
match the census.

## The sitting completed (2026-09-30 22:09:55Z)

Continuation 5 took `2x-light-receded` run 7, then every remaining pass in order, with **no
further stop**. At 22:09:55Z the orchestrator logged `ALL PASSES DONE`, and at 22:10:01Z it
restored mode 68 and verified it. The session trace (1,056 reads, 20 s apart) saw no HID input
from 16:16:17Z to the end; only the harness or Finder was frontmost.

**Every declared launch is admitted** under the hashed declaration (scenes `4aa06af9…`, bed
`53870f47…`, declaration `f04ae95b…`, no predeclaration), matching `dry-plan.json` run by run:

| Totals | Declared | Admitted |
| --- | --- | --- |
| dump launches / scenes | 8 / 447 | 8 / 447, 0 departures |
| capture launches | 80 | 80 |
| glass captures | 3,129 | 3,129 |
| no-glass references (run 1 of each bed pass) | 264 | 264 |
| sentinel captures | 48 | 48 |
| captures in all | 3,441 | 3,441 |

| Pass | Runs | Cells (run 1; runs 2–7) | Admitted |
| --- | --- | --- | --- |
| 8 dump passes | 1 each | 87, 92, 101, 107; 14, 16, 14, 16 scenes | 11:28:28 – 12:30:54Z (continuation 2) |
| 2x-light-active | 7 | 133; 87 | 12:31:01 – 14:15:49Z (continuation 2) |
| 2x-light-receded | 7 | 148; 92 | runs 1–3 by 15:08Z (continuation 2), runs 4–6 15:27:41 – 16:11:42Z (continuation 4), run 7 by 16:30:58Z (continuation 5) |
| 2x-dark-active / -dark-receded | 7 / 7 | 157; 101 / 175; 107 | 16:30:58 – 20:42:37Z |
| 2x sentinels (four) | 3 each | 2 | 20:42:37 – 20:49:26Z |
| 1x-light-active / -light-receded | 7 / 7 | 23; 14 / 26; 16 | 20:49:33 – 21:26:21Z (mode 69) |
| 1x-dark-active / -dark-receded | 7 / 7 | 23; 14 / 26; 16 | 21:26:21 – 22:03:10Z |
| 1x sentinels (four) | 3 each | 2 | 22:03:10 – 22:09:55Z |

**Quarantines**, all kept under their own names under `~/vitrea-w42/g1/run`:
1. `dump-2x-light-active/QUARANTINE-run-1-1790765998327680000`: Universal Control input took the focus (stop 1).
2. `dump-2x-light-active/QUARANTINE-run-1-1790767520002843000`: the same, with Universal Control reported off (stop 2).
3. `2x-light-receded/QUARANTINE-run-4-1790781804771531000`: another session's browser automation, counted at the close (stop 3).
4. `2x-light-receded/QUARANTINE-run-4-1790781952880634000`: the G1 worker's own launching shell, refused at the open (stop 4).
5. `2x-light-receded/QUARANTINE-run-7-1790784701958598000`: a calibration test suite's stub launch, refused at the open (stop 5).

**Elapsed.** Wall time was 11 h 22 min 9 s (10:47:52Z – 22:10:01Z). Continuation 5 alone ran
5 h 53 min 44 s. The capture passes ran at the rate `timing.txt` modelled: 2x dark active
2 h 1.5 min, 2x dark receded 2 h 10.1 min, each set of four sentinels about 6.8 min, and each 1x
pass 17–20 min.

**State at the close.** Display mode 68, verified. System TCC rows (read-only):
`dev.vitrea.reference-apple.w39` ScreenCapture auth 2 (2026-09-30 10:44:55Z);
`dev.vitrea.reference-apple` has no ScreenCapture row, and its Accessibility row is at auth 2;
`dev.vitrea.tccprobe` auth 0. The raw run root is 166 MB. `freeze.py verify` reads 1,818.

**Not yet done (phase 3, the parent's):** the archive's production, publication and replay;
the repeat bar; and the restore. For the restore, the user re-adds the original bundle alone.
Its positive check is compared against both recorded states of the canonical cell, `204f21f0…`
and `6c15311b…` (`prechecks/README.md`).

**Tracker items from the sitting.** (1) The census matches any process whose command line
merely names a browser, a capture tool or the harness: a `pgrep` pattern, or a test stub's fake
launch path. That caused stops 4 and 5. It fails safe, but it is brittle; it could match
executables rather than whole command lines. (2) The census excludes only the reader's own
ancestors. The orchestrator detaches with `setsid`, so the shell that launched it is not
excluded. (3) The orchestrator's per-pass `git add` drops each run's `driver-idle.log`, since
`*.log` is gitignored. The raw copy stays under the run root for the archive. (4) Universal
Control input reaches the Mac through a system agent that neither the census nor a
launch-time idle gate can see. A mid-run focus loss is caught only by the dump check or the
per-fixture pose attestation.
