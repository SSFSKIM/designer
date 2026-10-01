# W43 sitting tooling (charter G0 (d); G1a and G1b)

This is the instrument for W43's two native sittings
(`docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md`, Design "The two sittings").
It is derived from W42 G0's machinery
(`../../../2026-09-29-w42-g0-declaration/bed/sitting/`, which is not edited). Commit `ae073d8a`
copies W42's files byte for byte, and every change follows on top of it. G0 runs none of it
against the native side: no capture, no dump, no slider write, no display switch.

| file | what it is |
| --- | --- |
| `pass-spec.py` | the membership: reads a DECLARED plan (below); `order`, `plan`, `spec --sitting S --pass P [--run N]` |
| `sitting.py` | the driver: `plan` (dry), `pin-check`, `capture P [first] [last]`, `dump P [--rehearse]`, `wait-idle S`, `slider-as-found` / `slider-set X` / `slider-restore` (the orchestrator's), `publish P [--apply]`, `end-native APP` |
| `record-machine.py` | the machine read at every run's open and close; `census`, `launcher-chain`, `universal-control` |
| `sitting-orchestrate.sh` | one sitting in its one order, detached; the display mode and the slider restored on every exit |
| `run-sitting-w43.sh`, `collect-pass.py` | the entry point; the per-pass copy of attestations into the G1 evidence |
| `w43_archive.py` | `produce`, `verify-tree`, `pack`, `fetch`, `replay`: the archive of record |
| `timing.py`, `dry-plan-summary.py` | the sitting's length and dry plan, derived from the declared plan |
| `stand_in.py` | a G1a-shaped STAND-IN for the declaration (e) writes: test and rehearsal material only |
| `test_sitting.py`, `test_archive.py`, `test_timing.py` → `test-*.txt` | the suites: 47, 10 and 7 cases, stubs only |
| `red-green.py` → `red-green.txt` | each change red on W42's committed tools and green on W43's: 11 of 11 |
| `timing-stand-in.*`, `dry-plan-stand-in.*` | the deriver run on the stand-in: a rehearsal, not the sitting's numbers |

## The plan G0 (e) declares (the contract this tooling reads)

- **Files.** One plan per sitting: `../sitting-g1a.json` and `../sitting-g1b.json`, beside this
  directory in `bed/`. The declaration is `../../declaration.json`, hashed by
  `../../declaration.sha256`. It must hold an item `{"id": "sitting-g1a", "declared":
  {"planSha256": "<sha256 of the plan file>"}}`, and the same for `sitting-g1b`. `W43_SITTING=g1a`
  or `g1b` selects the plan for every tool.
- **Schema** `w43-sitting-plan-1`; the full form is in `pass-spec.py`'s docstring.
  - `sources` name each scenes file by repo-relative path and SHA-256: the canonical
    `apps/reference-apple/scenes.json` (version 8), W42's `scenes-w42-body.json` for its
    sentinels, and the wave-local probe and ladder file.
  - `passes` is the sitting's one order. A capture pass names its slider position `glass`,
    scale, pose, source, runs, protocol (`normal`, or `long` for W42's sentinels) and
    `profiles` (profile key → scene ids, captured every run). It may also name `run1Only`
    (references), `publish: true` (the canonical bed, for `materialize`) and `expect`
    (allowed frame SHA-256s per cell, e.g. the pose check's `204f21f0…` / `6c15311b…`).
  - A dump pass is a sentinel: `glass`, scale, pose, source, one `profile` and its `__rest`
    `scenes`.
- **Refusals.** `validate_plan` refuses, among others:
  - a profile key whose `-glass` token is not the pass's position (X6);
  - a receded id in an active pass, or the reverse;
  - a published pass with run-1-only cells, or with one run;
  - a non-`__rest` dump id;
  - an undeclared scene.
- **Before every launch**, `pin-check` requires all of these:
  - the plan and every source are committed at HEAD;
  - each source's bytes are the SHA-256 the plan names;
  - the declaration names the plan's SHA-256 and is itself hashed.

  `stand_in.py` builds a plan of this shape from committed files. It reproduces the charter's
  G1a membership exactly: 4,103 captures in 89 launches, 48 dump scenes, 562 published cells,
  two slider writes and four display switches. Its bridge cells and dump scenes are arbitrary
  picks; (e) declares the real ones.

## What W43 changes (each proved in `red-green.txt`)

1. **The census matches executables, not command lines** (`record-machine.py`; W42 G1 stops 4
   and 5).
   - A process counts by its executable image: libproc's `proc_pidpath`, falling back to
     argv[0] only where the image is unreadable. Any `Chromium` or `Google Chrome*` executable
     counts, and so does anything inside such a bundle (helpers, Chrome for Testing, the
     crashpad handler), a headless shell, and any `VitreaReference`.
   - Playwright and the capture scripts are node scripts, so for a node-family interpreter
     only, the script arguments are matched, by path component or exact file name:
     `compare.ts`, `capture-web`, `playwright*`, `@playwright`.
   - Red: W42 counted a `pgrep` shell, a `grep` line and a stub launch naming the harness.
   - Green: none of those counts, and all six real executable kinds still do.
   - A `compare.ts --skip-capture` still counts, since it is the script. The bar on
     whole-package test suites during a sitting stays.
2. **The launching chain is excluded.** Before it detaches, the orchestrator records its
   launching process and that process's ancestors (pid and start time) in
   `logs/launcher-chain-<epoch>.json`, and passes the file on in `VITREA_LAUNCHER_CHAIN`. A row
   is excluded only when both its pid and its start time match, so a reused pid still counts.
3. **The idle log is `driver-idle.txt`.** The repository ignores `*.log`, so W42 G1's 88
   committed runs hold no idle log. The watchdog's trace, `watchdog.txt`, is committed beside it.
4. **A watchdog runs during every launch, dumps included.** It reads the session every 5 s and
   trips on:
   - **HID input**: the idle reading falls behind the wall clock since the previous read, by
     more than 2 s;
   - **focus**:
     - in the active pose, any other frontmost app while the harness process still runs;
     - in the receded pose, anything replacing the app that was frontmost at launch,
       including the harness itself;
   - a lock, a permission prompt, or a session it cannot read.

   On a trip it kills the launch and the native app (by executable image) and quarantines the
   run, naming the reading. The rules match W42 G1's 1,056-read trace: receded passes read
   Finder throughout, active passes read the harness, and idle fell only at the two inputs.

   **What it cannot see:**
   - input that does not reset HIDIdleTime;
   - a focus change that returns within one 5 s period (the per-fixture pose attestation still
     reads every capture);
   - a key-window change inside the harness;
   - overlays that take no focus.

   **The Universal Control check** (`record-machine.py universal-control`) is recorded and
   summarised at the orchestrator's start. It is a report, not a gate. It reads the agent's
   process, the `Disable` key, Bluetooth, awdl0, Wi-Fi power and Handoff's flags. The input path
   counts as reachable when the agent runs and Bluetooth and awdl0 are up.

   On this Mac on 2026-10-01: the agent runs (pid 49435), the `Disable` key is absent, and the
   path is reachable. The check cannot tell:
   - whether a peer device is linked right now;
   - whether the agent forwards input with the feature off (W42 G1's stop 2 saw it do so);
   - whether `Disable` is where macOS 27 keeps the toggle. An absent key is not a reading, and
     confirming it needs System Settings.

   The user's prerequisite stands: Universal Control off on the capture Mac, and the other
   device away or asleep.
5. **The slider is declared per pass.**
   - **As-found.** The orchestrator records the as-found `NSGlassTintAmount` once per sitting
     root (`logs/slider-as-found.json`; a continuation keeps the first). The EXIT trap restores
     it: written back as the float it was, deleted if it was absent, no write if it already
     reads as found. The trap verifies it by read-back, beside the display mode.
   - **Writes.** Before each pass whose position differs, `slider-set` writes the slider and
     reads it back. It refuses while any harness or dump process is alive, checked by
     executable before and after the write, because a `defaults write` reaches only a freshly
     launched harness. The refusal stops the sitting (exit 9). Every write is logged in
     `logs/slider-writes.jsonl`.
   - **Per run.** The machine gate requires the read to equal the pass's position exactly, and
     the run refuses if the last logged write is another position.
   - **Seams.** `VITREA_DEFAULTS` is the `defaults` seam. The suites point it at a stub over a
     scratch file, and the proofs read the real default before and after (0.5 both times, read
     only).
6. **The dump sentinel** (`sitting.sentinel_check`) checks each surface's
   `inputBlurFillNormalOpacity` against the pass's position, at float32 precision. Each dumped
   scene must also read the requested pose (`isKeyWindow`, `appIsActive`), scheme and scale. A
   scene with no Normal input is a departure.
7. **The canonical publication path for side-bundle runs.**
   - `attest.read` carries what `materialize` reads: its provenance rules, and the fields its
     per-profile record keeps where all runs agree. The bundle fields name the SIDE bundle by
     path, identifier, cdhash, binary, minos and sdk, plus the SHA-256 and path of W39's
     `bundle-pin.json`.
   - A published pass derives one document for every run, so `passSpecSha256` agrees (rule 6).
     W42's run 1 carried references, which is why `materialize` refuses W42 G1's own committed
     attestations.
   - `publish P [--apply]` checks first that every run is admitted under the declaration,
     names the pin, and reads the pass's slider. It then runs
     `npx tsx cli/materialize.ts --run r1=… --profile <both keys> --frequency-settle` in
     `packages/calibration`, with `VITREA_SCENES` set to the canonical file. Without
     `--apply`, materialize writes nothing.
   - The canonical bed's `group` and `stack` components are now attested as
     PathAttestation.swift supplies them. W42's driver refused every `toolbar-group` and
     `glass-over-glass` capture, which would have quarantined every canonical pass.
8. **The archive stores each distinct frame once** (`frames/<sha256>.png`: captures and
   background rasters).
   - Per-cell records hold every run's membership and per-frame statistics, so a unanimous
     seven-run cell costs one frame.
   - `replay --deny-raw-root` recomputes everything from the archive alone.
   - W42's holdout redaction and receipt are dropped, because W43 seals no holdout. The
     canonical bed's held-out cells are published as fixtures (W29's practice), and the probe
     declares calibration and validation only (X46).
   - The tag is `w43-archive-<sitting>`.
9. **The dry plan and timing are derived from the declared membership.**
   - **Rates** come from W42 G1's 88 admitted runs (same machine, same bundle):
     - 2x: 11.43 s per run + 9.532 s per capture;
     - 1x: 10.88 s per run + 9.533 s per capture;
     - dumps: 0.77 s + 8.33 s per scene;
     - a display switch: 7.7 s.
   - **The slider write** is priced at 1 s, an assumption.
   - **On the stand-in**, the model gives 11.21 h (12.33 h with the charter's 10 % stop
     loss), against the charter's 11.26 h.
   - **Commands.** `timing.py --sitting g1a` and `dry-plan-summary.py --sitting g1a` price the
     real plan once (e) commits it.

## Kept from W42, and dropped

- **Kept:** the pin check before any launch and before every run; one read of every file,
  every run derived from it; the bounded idle wait before every launch; the machine gate,
  with every failing gate named; per-capture `hidIdleSeconds` ≥ 60; window and pose
  attestation; frame bytes bound at admission; quarantine without retry; the order gate; the
  detached orchestrator with an interruptible wait; launches only under the orchestrator.
- **Dropped:**
  - the TCC-refusal rehearsal: its premise, an ungranted side, ended when the side took the
    grant;
  - `rehearse-tints` stays absent, as in W42.

  A dump rehearsal remains: `REHEARSAL=1 PASSES="<dump pass> ..."`, in which the census is
  recorded rather than enforced. `STOP_AFTER=<pass>` cuts a sitting from the bottom of its
  order (X47).

## Runbook (G1a; G1b the same with `W43_SITTING=g1b`)

```bash
S=packages/calibration/results/2026-10-01-w43-g0-declaration/bed/sitting
W43_SITTING=g1a python3.12 $S/sitting.py plan --out /tmp/w43-g1a-plan     # executes nothing
W43_SITTING=g1a python3.12 $S/sitting.py pin-check
python3.12 $S/record-machine.py census                 # its own command, exited before the launch
python3.12 $S/record-machine.py universal-control      # read before the user's go
# the launch line holds only this (it detaches; follow logs/orchestrator-status.txt):
W43_SITTING=g1a VITREA_SITTING_DIR=~/vitrea-w43/g1a/run W43_EVIDENCE=<evidence dir> \
  W43_EVIDENCE_REPO=<checkout> bash $S/sitting-orchestrate.sh
# after the sitting: each published pass through materialize (dry, then --apply), then the archive
W43_SITTING=g1a VITREA_SITTING_DIR=~/vitrea-w43/g1a/run python3.12 $S/sitting.py publish bed-0.25-2x-active
python3.12 $S/w43_archive.py produce ~/vitrea-w43/g1a/run --sitting g1a --out ~/vitrea-w43/g1a-archive
```

A continuation is `START_AT=<pass> FIRST_RUN=<n>` against the same root, with every quarantine
kept under its own name.

**What counts in the census**, for concurrent workers:
- **Executables:** a Chromium, Google Chrome (any helper, Chrome for Testing, the crashpad
  handler inside the bundle), headless-shell or `VitreaReference` executable, wherever it lives.
- **Node scripts:** a node, tsx, bun or deno process whose script argument is `compare.ts`,
  `capture-web*`, or anything in a `playwright*` / `@playwright` package.
- **Not counted:** a command line that merely names these.

**Before the sitting:**
- Quit Google Chrome. The census read 8 Chrome processes on 2026-10-01.
- Hold browser automation in every other session.
- Bar whole-package test suites. This directory's own suites start processes under these
  names.
