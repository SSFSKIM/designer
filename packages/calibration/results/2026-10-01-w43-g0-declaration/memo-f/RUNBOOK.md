# Memo F — runbook: Apple's declared glass tree at nine slider positions

Charter `docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md` v1.2, clause 2, Design
"Memo F", G0 (c), X38, X42. Memo F reads the declared inputs of Apple's `glassBackground` filter
through the W39 side bundle's `dump-layers`, as W42's memo D did at one position. **It captures no
pixel, needs no Screen Recording grant and no X5 lift.** It needs the user's go for an idle window,
relayed by the parent. Until then nothing in this directory is run for real.

## What it changes, and how it is put back

- **The slider, machine-wide.** `NSGlassTintAmount` in the global domain is written at each
  position for the length of the window, so every app on the Mac draws its glass at that position
  meanwhile. Before the first write, the as-found value is read exactly (the exported plist value,
  or "absent") and fsynced to `as-found.json`. Every exit the process can see (completion, any
  refusal, any error, SIGHUP, SIGINT, SIGTERM) goes through one restore. The restore ends any harness
  process still running, writes the as-found bytes back (or deletes the key if it was absent), and
  verifies the exported value byte for byte. It then returns the display to mode 68, verifies it,
  and writes `restore.json`.
- **The display, for about four minutes at the end.** The last block (x = 0.25 at 1x) runs at
  displayplacer mode 69 and switches back to 68. The switch waits for 300 s of HID idle first, as
  memo D's did.
- Nothing else: no TCC row, no rebuild, no capture, no browser, no write to a checkout. The harness
  reads a copy of the canonical `scenes.json` v7 (pinned commit and SHA-256, in the run root) and
  an empty fixtures root.

## Before the go: the prerequisites (the user's, and other sessions')

- Universal Control **off**. No chat or input from the capture Mac during the window.
- Browser automation held in every other session. The cua helper's window quit.
- No other worker runs the calibration suite or any harness launcher (a stub launch reads as a
  harness).
- macOS still 27.0 (26A428); the display at mode 68; Reduce Transparency, Increase Contrast and
  Show Borders off. The driver checks all of these itself and refuses otherwise.

## The run

From the checkout that holds this directory, with the user's go relayed:

```bash
cd packages/calibration/results/2026-10-01-w43-g0-declaration/memo-f
python3.12 -B memo_f.py run ~/vitrea-w43/memo-f/run-$(date -u +%Y%m%dT%H%MZ)
tail -f ~/vitrea-w43/memo-f/run-*/logs/status.txt          # it detaches into its own session
```

- **Preflight, before any write:** the build, the three accessibility settings, display mode 68,
  and the side bundle's binary, cdhash and identifier against W39's `bundle-pin.json`. It also
  requires no harness process alive, the screen unlocked, no permission prompt, and Universal
  Control not frontmost. Then it waits for ≥ 300 s of HID idle, and records the as-found value.
- **Ten blocks, in priority order** (`plan.json`): x = 0.5 (the control: every surface must
  reproduce memo D exactly), 0.25, 1, 0, 0.75, 0.125, 0.375, 0.625, 0.875 at 2x, then 0.25 at 1x.
  Each block makes one slider write, read back. It then runs four fresh launches: light active,
  light receded, dark active, dark receded.
- **The scenes:** six shapes on dark-solid, s = 44, 64, 80, 96, 128 and 160 (memo D's strata and
  every w-test shape). At 0.25, 0 and 1, two more: rrect-md on photo and on the checkerboard, the
  backdrop control.
- **Every launch:** HID idle ≥ 60 s (otherwise a pause until 300 s; all pauses share one 3 h cap),
  no harness alive (a running app has already read its preferences, so only fresh launches count),
  the X6 read with the slider at x, `open -W` exactly as memo D launched it, a 10 s session trace,
  memo D's overrun bound, the closing read, and `check`. `check` requires exactly the declared
  scene files and the declared scheme, scale, build and pose in each. Every surface must read
  `inputBlurFillNormalOpacity` = x (X42's tree reading). At x = 0.5 there must be zero departures
  from memo D.
- **Totals:** 40 launches and 264 scene dumps. **About 43 minutes of dumps** (W42 G0's measured
  rates plus the gates), **about 48 minutes from the moment the Mac goes idle.**

## If it stops

A refusal quarantines that launch under its own name (`runs/QUARANTINE-<label>-<ns>/`), restores,
and exits 3. Nothing is retried. `logs/status.txt` names the cause. A continuation is the parent's
explicit act, after the cause is gone:

```bash
python3.12 -B memo_f.py run <the same run root> --continue
```

It re-reads the slider, which must equal the recorded as-found value. It skips every admitted
launch and keeps the quarantines. Exit 7 means **RESTORE FAILED**: stop and restore by hand before
anything else.

**By hand** (only after a SIGKILL, a power loss or exit 7): `python3.12 -B memo_f.py restore <run
root>` does the same restore from `as-found.json`. Failing that, write the `xml` value recorded
there with `defaults write -g NSGlassTintAmount '<real>…</real>'` (or `defaults delete -g
NSGlassTintAmount` if `present` is false). Then run `/opt/homebrew/bin/displayplacer
"id:7709FD0F-F423-4277-B0C8-7CA94F85723A mode:68"`.

## After it completes

1. `restore.json` reads `verified: true`; `defaults read -g NSGlassTintAmount` and `displayplacer
   list` agree with it.
2. The reading:
   `python3.12 -B memo_f_read.py <run root> --out ../memo-f-reading`. It produces `tables.json`
   and `reading.txt`: the inputs that move with x per endpoint, memo D's laws and constants at
   each x, the ramps with their piecewise-linear reading, and the backdrop and scale controls.
3. The record. The run root stays in scratch, as memo D's did. `python3.12 -B record.py <run root>`
   refuses unless the restore verified and the slider reads its as-found value now. It writes the
   run's SHA-256 manifest and copies the attestations into `run/` (`preflight.json`, `as-found.json`,
   `restore.json`, every launch's `machine-*.json`, `check.json`, `admission.json` and session
   trace, and `logs/`). It also runs the reading into `reading/`. Commit both; the dumps themselves
   stay behind the manifest. Step 2 is then the same reading, already done.
4. The memo. The numbers are pointers (X38). They state the w-test's prediction in the
   declaration before it is hashed (clause 2), and the pixels referee them.

## What was proved before the window

- `proof.txt` (`proof.py`): 86 expectations over 31 cases, all holding, re-run after the window. The cases run on stub
  tools, with the slider in a sandbox defaults domain through the real `/usr/bin/defaults`. The
  harness is a re-signed copy of `/bin/sleep` that really runs, and the dumps are memo D's own,
  patched. Green: as-found 0.5, absent, and an odd double (0.5459057092666626), each restored
  exactly, the 1x block at mode 69, x = 0.5 reproducing memo D, one write per block. Red: wrong
  build, accessibility on or unset, pin mismatch, mode 69 at start, Universal Control frontmost,
  prompt, locked screen, idle cap, a live harness before the first write, an as-found string, a
  harness that outlives its launch, a dump at the previous slider, a lost focus, a memo D departure
  at 0.5, a missing scene, a failed launch, a display switch that does not take, a failed restore
  (exit 7, then `restore` by hand), SIGTERM, SIGINT during the 1x block, SIGHUP, this runbook's own
  detached command and a detached child refusing a dirty root, a continuation
  (and its refusal when the slider is not at the as-found value), a run root inside the checkout,
  a real tool in the stub directory, and the shortened waits outside stub mode. The proof read the
  machine's real slider (0.5, a real) and display mode (68) before and after, and both were
  unchanged; it never wrote either.
- `proof-read.txt` (`proof_read.py`): 11 of 11. Memo D's own dumps read as a 0.5 run (nothing moves,
  zero departures, 1x against 2x exactly memo D's four device-pixel terms). A stub run (exactly the
  stubbed fields move, with their slopes). W29 G0's one-scene sweep (W29's committed table
  recovered).

## A pointer already on record (W29 G0's sweep, `w29-sweep-reading/`)

Read by the same reader, W29's dumps of light active photo rrect-md at x = 0, 0.25, 0.5 and 1
move four fields. Three are the ones W29 tabled: Normal = x; the face fill's alpha 0, 0.1, 0.2,
0.5; Lighten 0.675, 0.7875, 0.9, 0.9. **The fourth is the backdrop layer's capture scale, 0.5 at
x ≤ 0.5 and 0.125 at x = 1.** Nothing else moves there: no blur radius or opacity, no face
matrix black, white or saturation, no MaxLuma or clamp. It is one scene in one endpoint. Memo F
reads the rest, and the ladder's x = 1 cells will be read at that coarser capture if it holds.
