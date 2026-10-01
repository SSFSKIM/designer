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
| `test_sitting.py`, `test_archive.py`, `test_timing.py` → `test-*.txt` | the suites: 66, 11 and 7 cases, stubs only |
| `red-green.py` → `red-green.txt` | each change red on the tools before it (W42's committed ones; W43's as accepted at `d92190b4` for the rulings 10 and 11; the reviewed head `d32cf72d` for the review's 1b and 12; `materialize` alone for 7c) and green on W43's: 17 of 17 |
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
  - Every capture pass whose role starts `bridge-` carries a `bridge` block (change 10). It
    holds `stop` (true on `open-*` passes, false on `close-*`) and `cells`: exactly the cells
    the pass captures, each with its `reference`. A canonical cell's reference is
    `{sha256, path}` of its committed 0.5 fixture; a W42 sentinel's is `{sha256, archive:
    "w42-archive"}`, the frame its long-protocol rows settled on. An optional `bars` names W42
    G1's `bar.json.gz` by the SHA-256 of its JSON and a protocol.
  - Every `close-*` pass of role `bridge-w42-sentinel` declares `runAfterCut: true` (change 11).
    No other pass may carry the key, and those passes are the order's tail.
- **Refusals.** `validate_plan` refuses, among others:
  - a profile key whose `-glass` token is not the pass's position (X6);
  - a receded id in an active pass, or the reverse;
  - a published pass with run-1-only cells, or with one run;
  - a non-`__rest` dump id;
  - an undeclared scene;
  - a bridge pass without its `bridge` block, with the wrong `stop`, or whose cells are not
    exactly its captured cells;
  - a closing W42 sentinel bridge without `runAfterCut: true`, or any other pass carrying it.
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
     only, its ENTRY script is matched, by path component or exact file name: `compare.ts`,
     `capture-web`, `playwright*`, `@playwright`. The entry script is the first non-option
     argument of the kernel's exact argv (so a path with a space stays whole). The values of
     options that take one are skipped (`--require r.js`, `--import x.mjs`), the argument after
     `--` is the script, and `-e` / `-p` carry no script. Every later argument is the program's
     data.
   - Red: W42 counted a `pgrep` shell, a `grep` line and a stub launch naming the harness.
     Before the review's P2, W43 also counted `node benign.js …/playwright-core/cli.js`, a
     benign script handed a Playwright path as data (scenario 1b).
   - Green: none of those counts, and all six real executable kinds still do, as do Playwright
     as the entry and the tsx child's `--require … --import … cli/compare.ts`.
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
   run, naming the reading. In a sitting it polls every 5 s, so a run is stopped within about
   5 s of the event, plus the kill. The 0.3 s in `red-green.txt` is the test's own poll period,
   not a sitting's. The rules match W42 G1's 1,056-read trace: receded passes read Finder
   throughout, active passes read the harness, and idle fell only at the two inputs.

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
     attestations (scenario 7, which fails on the differing declarations).
   - The missing pin is a separate check, isolated in scenario 7c. The runs agree on one
     declaration and their `attest.read` carries no bundle field. `materialize` alone, the path
     W29 published by, writes a profile record naming no bundle; `publish` refuses the runs
     before materialize runs.
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

The coordinator then ruled two more, after the first 11 of 11:

10. **The opening bridge's verdict is charter clause 3's metric, run by run**
    (`sitting.bridge_verdict`).
    - **The rule.** Every run of every bridge cell must agree with its reference: byte- or
      pixel-identical, or else every region median within max(1 code, bar). The regions are
      W42's instrument, unchanged, as G0 (b) read them: `forward.Cell` at the cell's own
      geometry, masks `n` and `w` active and `n` receded, a per-channel median per population.
      The bar is the cell's measured repeat bar from the declared bar file, or the 0.5 floor
      where none was measured, so the tolerance is 1 code everywhere W42 measured.
    - **What disagrees.** A region the reference carries but the frame does not (no opaque pixel
      in it, or a frame of another size), and a cell with no region statistic at all, which
      can then agree only by identity.
    - **On (e)'s declared cells** (read 2026-10-01, `sitting-g1a.json` at `e94b2ed2`):
      - `hc-text__rrect-sm__rest`, in the active pose at both scales, has no region statistic
        under either mask, so it bridges only by byte or pixel identity. (e) has since replaced
        it with `hc-text-28__rrect-md` (`333ac8b1` on `w43-g0-decl`), and its generator now
        refuses an opening canonical cell without a region statistic.
      - The active capsule cells and `f-impulse-rrect-md__rest` read mask `n` only, because
        the wide mask is empty at their spans.
      - Every other cell reads both masks when active, or `n` when receded.
    - **Before any launch,** the references are read and checked by SHA-256. Fixtures come from
      the repository; w42-archive frames come from the store named by `W43_BRIDGE_REFERENCES`,
      which `sitting.py bridge-references <w42-archive tree> --out <store>` fills from the
      verified archive (probe role only, through W42's guarded Reader).
    - **Each run** writes `bridge.json` and records the verdicts in its admission.
    - **On a disagreement.**
      - At an opening (`stop: true`), the run stays admitted as evidence and the driver exits 10.
        The orchestrator stops the sitting before any capture away from 0.5. The run no longer
        counts toward the order, so nothing proceeds from it under this declaration.
      - At a close (`stop: false`), the disagreement is recorded and nothing is voided.
11. **A cut never drops the close.**
    - **The cut.** After a `STOP_AFTER` cut the orchestrator restores the slider to its as-found
      value (logged as a write) and the display to mode 68. It then runs every `runAfterCut`
      pass after the cut, in order, with `W43_CUT_AFTER` set.
    - **The driver** lets only those passes past the passes the cut dropped. The dropped passes
      can never be taken later, because a later pass has started.
    - **The archive.** `w43_archive.py produce --cut-after <pass>` archives a cut sitting and
      names the dropped passes. It refuses one of them that ran.

The independent review of `6cb112d5..d32cf72d` found two more, both fixed (scenarios 1b and 12,
red on the reviewed head):

- **P1, the EXIT trap could be cut short.** A HUP, INT or TERM during the trap's restoration ran
  the cancel handler, whose `exit` inside the trap ended the shell without re-running it. The
  display was left at mode 69, unverified, with no RESTORE FAILED. The restoration now ignores
  the three signals for its whole duration (its children inherit that), runs once, and exits
  only after its verification lines are logged. A refused slider write is RESTORE FAILED and
  exit 7, with the display still restored and verified.
- **P2, a later argument counted as a node script.** Change 1 now reads the entry script only.

## Kept from W42, and dropped

- **Kept:** the pin check before any launch and before every run; one read of every file,
  every run derived from it; the bounded idle wait before every launch; the machine gate,
  with every failing gate named; per-capture `hidIdleSeconds` ≥ 60; window and pose
  attestation; frame bytes bound at admission; quarantine without retry; the order gate; the
  detached orchestrator with an interruptible wait; launches only under the orchestrator.
- **Dropped:**
  - the TCC-refusal rehearsal: its premise, an ungranted side, ended when the side took the
    grant;
  - `rehearse-tints` stays absent, as in W42, and no tint gate replaces it (the coordinator's
    ruling, 2026-10-01). W29 ran it before each receded pass, replaying the harness's
    end-of-run tint attestation over the committed fixtures. Two reasons it is not carried:
    - the bridges' four tinted cells (`photo__capsule-button` and
      `checkerboard__capsule-button` with the orange tint, in both poses) are read by clause
      3 against W29 fixtures that the original harness already tint-attested, which is the
      stricter check;
    - a pre-flight over the 0.5 fixtures says nothing about 0.25 pixels.

    No untinted twins are added to the bridges, and (e) records this as a declared non-gate.

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
# the W42 sentinels' reference frames, from the verified w42-archive (probe role only):
W43_SITTING=g1a python3.12 $S/sitting.py bridge-references "$(python3.12 \
  packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting/w42_archive.py fetch \
  --asset w42-archive-1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014.tar.zst \
  --sha256 1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014)" --out ~/vitrea-w43/references
# the launch line holds only this (it detaches; follow logs/orchestrator-status.txt):
W43_SITTING=g1a VITREA_SITTING_DIR=~/vitrea-w43/g1a/run W43_BRIDGE_REFERENCES=~/vitrea-w43/references \
  W43_EVIDENCE=<evidence dir> W43_EVIDENCE_REPO=<checkout> bash $S/sitting-orchestrate.sh
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
