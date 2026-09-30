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
