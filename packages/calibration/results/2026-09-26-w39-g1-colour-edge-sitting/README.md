# W39 G1 — the colour-and-edge sitting (c9a §5.185)

The operational index of the sitting. Charter:
`docs/doperpowers/specs/2026-09-26-w39-colour-edge-capture.md`; runbook: G0's evidence README
(`../2026-09-26-w39-g0-colour-edge-bed/README.md`). Raw runs live under `~/vitrea-w39/run/`
on the capture machine (X12) and are never committed; this directory holds the attestations,
driver logs and admissions of every pass, committed after each one.

## Worker change (X9 record)

The first G1 worker ran on the frontier rung and was cut off by that rung's usage limit after
attempt 1 of the refusal rehearsal. From attempt 2 on, this gate is continued by a second
worker in the same worktree and branch, from the committed head `17e54807`, on the parent's
explicit instruction. Nothing was retaken over: every earlier artefact stands as committed.

## Step 0 — preconditions (`setup/`, `preconditions/original-positive-1/`)

Worktree installed and built (`setup/install-build.txt`); freeze 1,818
(`setup/freeze-verify.txt`). The ORIGINAL granted bundle
(`apps/reference-apple/build/VitreaReference.app`, never rebuilt) captured the 27-only 2x light
checkerboard capsule cell at mode 68 with explicit scratch roots: `materialRendered`,
`presentedActive`, `deterministic` true, `repeatNoise` 0 (`admission.json`; the script that ran
it is `setup/original-positive.py`). `setup/continuation.json` records that the worktree session
switch was refused and absolute paths were used instead.

## Step 1 — the TCC-refusal rehearsal (`rehearsal/`)

### Attempt 1 (first worker): active-2x QUARANTINED as prompt-pending

`rehearsal/attempt-1/active-2x/`. The side bundle attempted the capture and printed the
harness's TCC-gate sentence, with no manifest, no PNG and no staging directory — but a
`universalAccessAuthWarn` window (a Screen Recording prompt for the side bundle's first SCK
call) appeared during the launch, so the driver classified the run `prompt-pending` and
quarantined it (`refusal.txt`; raw at
`~/vitrea-w39/run/held/attempt-1/rehearsal-g1/rehearsal-active-2x/QUARANTINE-run-1-1790367690162824000`
after the relocation below). Nobody clicked Allow. The user dismissed the prompt with **Deny**.
The system TCC database then read (read-only; `rehearsal/attempt-2/tcc-before.json`):
`dev.vitrea.reference-apple` auth 2 (2026-09-23 21:18:31Z), `.w34` auth 0, `.w39` **auth 0,
last modified 2026-09-25 20:21:29Z** — the denial the prompt's answer wrote. No prompt was on
screen before attempt 2 (`rehearsal/attempt-2/session-before-attempt.json`).

### Relocation of attempt 1's directories (`rehearsal/relocation.txt`)

`sitting.py` refuses an evidence root that has a direct child named `rehearsal-*` ("an evidence
root holds no rehearsal"), and attempt 1 had used `~/vitrea-w39/run/rehearsal-g1` as its
rehearsal root and `~/vitrea-w39/run/rehearsal-logs` for driver logs — both direct children of
the evidence root. They were MOVED, not deleted and not edited, to
`~/vitrea-w39/run/held/attempt-1/{rehearsal-g1,rehearsal-logs}`. The file records the command,
`find` listings before and after, and the SHA-256 of all 81 moved files before and after
(identical). The gate itself is unchanged.

### Attempt 2 (second worker): all four passes `refused-tcc`

Fresh rehearsal root `~/vitrea-w39/run/held/attempt-2/rehearsal-g1`, driver logs beside it in
`rehearsal-logs/`; `rehearsal/attempt-2/collect.sh` copied each run's attestations here (not its
generated background PNGs) with a read-only TCC read taken right after. In order, each
`VITREA_SITTING_DIR=… run-sitting-w39.sh <pose> <scale> --rehearse-refusal`, one commit each:

| Pass | Mode (open/close) | Outcome | Capture attempted | TCC-gate sentence | Manifest / PNG / staging / new window |
| --- | --- | --- | --- | --- | --- |
| active-2x | 68 / 68 | refused-tcc | yes | yes | none |
| active-1x | 69 / 69 | refused-tcc | yes | yes | none |
| inactive-1x | 69 / 69 | refused-tcc | yes | yes | none |
| inactive-2x | 68 / 68 | refused-tcc | yes | yes | none |

Every opening read: 27.0 / 26A428, tint 0.5, RT/IC/Show Borders 0, the side pin (cdhash
`be258cbf…`, binary `02052b17…`), zero foreign capture processes, no prompt on screen and
≥ 60 s HID idle; every closing read agreed. The system TCC rows were unchanged across all four
(`.w39` auth 0 at 20:21:29Z; the original auth 2): the recorded denial suppresses the prompt,
as the harness README said it would. The display mode was switched between passes with
`displayplacer "id:7709FD0F-… mode:69|68"` and read back by each run's own machine read.
`argparse-usage-error-no-launch.txt` is a shell-quoting mistake of this worker's before the
active-1x launch: `sitting.py` rejected the argument at parsing, before creating any directory
or reading the machine; nothing launched and no run was consumed.

The rehearsal is complete: the ungranted side bundle is refused by the TCC gate in both poses
at both scales, with the real run-1 argv.
