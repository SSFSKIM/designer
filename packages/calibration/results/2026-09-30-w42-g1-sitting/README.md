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
