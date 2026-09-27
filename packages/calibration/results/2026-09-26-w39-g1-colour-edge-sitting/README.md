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

## Step 2 — the grant switch (the user's hand)

"Ready for the grant switch" went to the parent at head `5e3a8064`, with the side app's path,
its cdhash `be258cbfc53e5cec6b49ecdec01f126872400b29` and the Settings steps. The user made the
switch and left the machine. The parent then read the system TCC rows (read-only, 03:05:26Z):
`dev.vitrea.reference-apple.w39` auth **2**, `.w34` auth 0, and **no row at all** for the
original `dev.vitrea.reference-apple`. Its Screen Recording row was removed, not merely turned
off. Its separate Accessibility row (auth 2, 2026-08-28) is untouched. Nobody else touched the
GUI.

## Step 3 — positive checks after the switch (`grant/`)

`grant/grant-check.py side|original <attempt>` is step 0's one-cell construction: the canonical
27-only 2x light checkerboard capsule, at mode 68, with explicit scratch roots under
`~/vitrea-w39/run/grant-checks/`. It applies the sitting's own machine and session gates and
reads the TCC rows before and after each attempt. It classifies the outcome rather than asserting
it. `grant/when-idle.sh` delays a launch until read-session reports ≥ 75 s of HID idle and no
prompt window. The command's own gates still decide.

| Attempt | Outcome | presentedActive | materialRendered / deterministic / repeatNoise | PNG vs. committed canonical fixture |
| --- | --- | --- | --- | --- |
| `side-positive-1` | captured-inactive | **false** | true / true / 0 | 22,457 px differ (max 100): the inactive pose |
| `side-pose-check-2` | **captured-active** | true | true / true / 0 | **byte-identical**, SHA-256 `6c15311b…` |

As in W34 (its Decision Log 4 and §5.174 §6), the side bundle's first launch after the grant
was repeat-stable but **inactive**. That attempt is kept. The second of the three authorised
pose checks attested active, and its PNG is byte-identical to the committed macOS 27 2x light
fixture, as W34's side capture was. The third check was not needed.

One observation is new. During `side-positive-1` a **`UserNotificationCenter` window at window
level 8** (a system modal alert) appeared and took the front. It is the most likely reason that
launch attested inactive, though the cause is not established. The window stays on screen. Its
text cannot be read without granting this shell a capture or automation permission, which would
itself prompt, so it was not read and nothing clicked it. `side-pose-check-2` activated past it
and attested active with no new window. The sitting's gates list only `universalAccessAuthWarn`
as a prompt owner, and this window is not treated as one. Every active capture still attests its
own `presentedActive`, and `validate_manifest` refuses a run if any cell attests otherwise, so a
stolen focus quarantines a run rather than passing silently. `grant/session-after-checks.json`
records the window still present after the checks.

**The original's check is the TCC read, not a launch (the parent's ruling).** With no TCC row,
launching the original would raise a new permission prompt that nobody is present to dismiss, and
that prompt would block every later launch. So the original was **not launched**. Its state is
recorded by the read-only system TCC read (`grant/tcc-after-checks.json`): no
`kTCCServiceScreenCapture` row for `dev.vitrea.reference-apple`, meaning not granted. At this
moment the side holds the only vitrea Screen Recording grant. At wave close, restoring the
original follows the harness README's add recipe, with a positive check of both bundles
(Decision Log 4).

Step 0's original capture, for the record, differs from the canonical fixture at 115 pixels by
≤ 2 codes (`grant/side-canonical-comparison.json`). Step 0's admission required only its
attestations, which all held. This is recorded as a reading, not a finding about either bundle.

## Step 4 — the preflight and its verdict (`preflight/`, `attest/preflight-*`)

Evidence root `~/vitrea-w39/run`. Its direct children are `grant-checks`, `held`, `logs`,
`preconditions` and `setup`; none is a rehearsal. Commands:
`VITREA_SITTING_DIR=~/vitrea-w39/run preflight.py run 1` at mode 69, then `run 2` at mode 68.
Each pass is two sitting runs: run 1 is the nine geometries × glass/opaque, and run 2 is the
phase-zero pair repeated at the pass's end. Every run was admitted: **40 captures**, 18 + 2 per
scale, with no quarantine. `tools/collect-pass.py` copied each run's machine and session reads,
`launch.json`, `admission.json`, the driver log and a distilled record (`runs.json`: manifest
SHA-256, fixture count, capture times, protocol) into `attest/<pass>/`. Manifests, capture logs
and PNGs stay producer-only under the run root. Then `preflight.py verdict --root ~/vitrea-w39/run`
ran **once**. Its output is `preflight/preflight-verdict.json`, byte for byte (SHA-256
`ffa40971…4391b`), with `verdict-summary.json` as a distillation.

**Verdict: branch `neither`. Axes x and y are both `unreachable`, failing at 1x and 2x. The
admitted phase allowlist is empty** (derive(reachable) − derive(none) = ∅). So the bed runs
without phase variants, exactly as W34 §5.174 §7 found on its path.

| Scale / axis | Opaque near identical | Opaque far states | Glass near (D_int_near; max pair) | Glass far states (phase → state) | RSS shift / amplitude (ratio; amp converged) | Fitted offsets (device px) | Rank; condition | LOPO |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1x x | yes | **2** | 0; 0 | **2** (0,0,1,1) | 683.5 / 50,708 (0.0135; **no**, 200 alternations) | 0, −0.063, 0.937, 0.937 | 22/22; 4.74e5 | pass |
| 1x y | yes | **2** | 0; 0 | **2** (0,0,1,1) | 268.0 / 38,507 (0.0070; no) | 0, −0.188, 0.813, 0.813 | 22/22; 856 | **fail** |
| 2x x | yes | **2** | 0; 0 | **2** (0,0,1,1) | 1,004 / 56,215 (0.0179; no) | 0, −0.094, 0.921, 0.922 | 40/40; 4.31e3 | pass |
| 2x y | yes | **2** | 0; 0 | **2** (0,0,1,1) | 442.1 / 42,659 (0.0104; no) | 0, −0.188, 0.813, 0.813 | 40/40; 1.17e3 | **fail** |

The decisive reading is the state count. Requested quarter-device-pixel phases {0, ¼} and
{½, ¾} collapse to **two byte states** on both the opaque control and the glass, at both scales
and on both axes. The fitted offsets are a whole-pixel step (about −0.06…−0.19 and +0.81…+0.94),
not a monotone quarter-pixel ramp, so criterion (b) fails everywhere. Near-edge invariance holds
exactly: D_int_near = 0 and max pairwise 0. The integer size controls gave D_int_far = 0. The
end sentinel is byte-identical at both scales, so there is no drift and the verdict is not
UNMEASURED. Criterion (a) reads false even at ratios of 0.007–0.018, because the amplitude fit
reached its 200-alternation cap without converging, and the declaration makes a non-converged
alternative "not established". That is recorded, not re-tuned, and it changes nothing: the
state count and monotonicity already refuse both axes. No fallback actuator was tried (charter
clause 4).

## Step 5 — the passes (`attest/<pass>/`, `tools/sitting-orchestrate.sh`)

`tools/sitting-orchestrate.sh` runs the passes in the declared order, one driver invocation
(all runs) per pass. Before each pass it sets the pass's display mode, reads it back and waits
for ≥ 75 s of HID idle. After each pass it reads the mode back, runs `tools/collect-pass.py`
and commits. Any failure stops it, and it never retries. Its first stop is recorded below.

### Stop 1 — Google Chrome launched during active-1x run 1 (`stop-1/`)

active-1x run 1 (332 captures at mode 69, 03:18:20Z–04:11:01Z) was **quarantined by the
driver**: `pose attestation failed` (`attest/active-1x/QUARANTINE-run-1-1790395862598343000/`;
raw run at `~/vitrea-w39/run/active-1x/QUARANTINE-run-1-1790395862598343000`).
`stop-1/pose-timeline.json` holds only attestation metadata: capture time, `presentedActive`,
`hidIdleSeconds`, and no pixel statistic. It reads **172 captures active, all before
03:45:30Z, and 160 inactive, all from 03:45:40Z on**, with none out of place on either side.
Per `ps`, **Google Chrome** (`/Applications/Google Chrome.app`, pid 317) was **launched at
03:45:37Z**, and it is the frontmost application from then until now
(`stop-1/chrome-process.txt`, `stop-1/session-after-stop.json`).

HID input happened at about 03:45:46Z. The capture at 03:45:49Z records `hidIdleSeconds` 3.1,
and six captures carry idle under 60 s. The session has been idle since. By 04:36Z the
`UserNotificationCenter` alert seen at the grant check is **no longer on screen**. Who launched
Chrome, and how the alert was dismissed, is not known to this worker; nothing here launched,
clicked or closed either. The driver's census regex (`Chromium|playwright|…`) does not match
"Google Chrome", so the opening and closing reads count 0 foreign processes. The brief,
however, counts a background Chrome as foreign (X6). Chrome is also what took the harness's
activation, and so the active pose. The run is therefore quarantined for two reasons: its own
pose gate, and a foreign process.

Nothing was retried. `stop-1/stop-after-run1.sh` was armed to interrupt this worker's own
driver at the run boundary, but it was not needed: the driver refused run 1 itself and exited,
and the orchestrator committed the stop (`986aee2e`). No further run started. Chrome was not
touched: this worker terminates no other session's process.

**To continue**, two things are needed. First, Chrome quit by whoever owns it. Second, an
explicit, recorded operator continuation: `active 1` again takes a fresh run 1, because the
quarantine is already preserved under its own name and the driver refuses to overwrite anything.

**A gap found in passing.** The sitting gates HID idle before each LAUNCH (≥ 60 s), and the
harness records `hidIdleSeconds` on every fixture. But `validate_manifest` does not check the
per-capture idle, so a run whose middle captures were taken under HID activity could be
admitted if its pose attestations still held. Here the pose gate caught it. Whether per-capture
idle should be a gate is logged for the parent, not changed mid-sitting.

### G1 gate corrections after stop 1 (the parent's continuation; `gate-corrections/`)

The parent ruled explicitly and recorded it. The parent quit Chrome under the user's standing
authorisation: pid 317's parent was launchd, and no automation parent was found. The user was
told to stay off the machine. The preflight verdict is accepted as Decision Log 3, with the
amplitude fit's non-convergence at its 200 cap noted as a limitation that changes nothing. Two
refusals were added, both stricter; nothing was loosened:

1. **Foreign census by name** (`record-machine.py` `FOREIGN` / `is_foreign`). The census now
   also refuses any Google Chrome, Chrome Helper, Playwright or headless-shell process, beside
   its earlier criterion. The Docker Electron crash handler and ordinary processes are not
   matched. The test takes its command lines from the stop-1 `ps` reading.
2. **Per-capture HID idle is an admission check** (`sitting.py` `validate_manifest`). A run
   whose manifest records any capture with `hidIdleSeconds` below 60, or with the field missing,
   is refused, and so quarantined. Before this, the 60 s idle was a launch gate only.

`test-sitting.py` now runs 29 tests and passes (`gate-corrections/test-sitting.txt`). The other
six W39 Python suites pass unchanged. The four admitted preflight runs re-validate under the
corrected gate, with minimum per-capture idle 257–640 s (`admitted-runs-recheck.json`). The
census reads 0 with Chrome gone (`census-now.txt`).

### The step 6–7 producer tools, tested before the passes (`tools/`)

- **`tools/report-bars.py`** computes the repeat bar per cell, member, bin and channel from the
  archive of record, through the guarded reader. The formula is 0.5 + ½ × the largest pairwise
  run separation. A run contributes the deep body's per-channel median and each measured bin's
  mean. An UNMEASURED bin in any run makes that bin's bar UNMEASURED. The deep spatial min/max
  is kept separately. The normal and long protocols are separate strata. Only calibration and
  validation are read; asking for the holdout refuses at the command.
- **`tools/materialize-probe.py`** builds the probe bed through the canonical
  `cli/materialize.ts` and partitions it by identification role, with holdout public entries
  stripped as in W34.

**A finding from the test, before any use.** `materialize.ts` refuses runs that read two
declaration digests (`run-provenance.ts` rule 6). A W39 bed pass's run 1 reads a different
declaration from runs 2–7 by construction, because `pass-spec.derive` adds the colour
references to run 1 alone. Handing it all seven runs would therefore have refused every pass
at step 7. The two declarations are identical on every shared cell (scenes, components,
backgrounds, canvas), and runs 3–7 equal run 2 exactly, as checked against pass-spec for all
four passes. So the materialiser gives `materialize.ts` the six runs 2–7, which read one
declaration. It then folds run 1 in as the seventh vote on each shared cell:
- where run 1 holds the published state, the cell is recorded as agreeing;
- where it differs, the cell is kept only if runs 2–7 were unanimous (six against one, which no
  seven-run plurality could overturn), and the difference is recorded;
- anything else refuses, for a ruling.

Run 1's reference-only cells are then added from run 1, marked `singleRun`. The canonical
`materialize.ts` is not edited. The archive and the bar use every run, run 1 included. This
choice affects only which bytes the probe bed publishes, and it is recorded for the parent to
overrule before step 7.

`tools/test-g1-tools.py` passes all 6 tests (`tools/test-g1-tools.txt`) on the admitted
preflight runs:
- the materialiser end to end over each scale's runs, with fold agreement, a recorded
  difference, a refused disagreement, run-1-only addition, partition, holdout stripping and the
  declaration premise;
- report-bars over a real archive written by `w39_archive.produce` from the byte-identical
  phase-zero glass runs, where every bar is exactly 0.5;
- the same archive with one run lifted by three codes, where the deep bar is 2.0;
- the holdout refusal.

### Continuation after stop 1 (the operator's explicit, recorded act)

The parent's message is the continuation: Chrome was quit by the parent, the user is off the
machine, and the pass order restarts with a **fresh active-1x run 1**. The quarantine keeps its
own name, and active-2x, inactive-1x, inactive-2x and the sentinels follow in order. The session
read at continuation is `stop-1/session-at-continuation.json`. The census, under the corrected
gate, reads 0.

### Stop 2 — active-1x run 7: HID input, then the system alert took focus (`stop-2/`)

The restarted pass admitted **runs 1–6 of active-1x**: 332 + 5 × 206 captures at mode 69, every
one under the corrected gates (`attest/active-1x/run-{1..6}/`). **Run 7** (206 captures,
07:59:45Z–08:32:16Z) was **quarantined by its own pose gate**
(`attest/active-1x/QUARANTINE-run-7-1790411537373327000/`; raw run under the same name).
`stop-2/pose-and-idle-timeline.json` holds attestation metadata only. It shows two independent
causes, either of which refuses the run under the corrected gates:

1. **HID input at about 08:10:44Z.** Six captures, 08:10:51Z–08:11:39Z, record `hidIdleSeconds`
   of 7.1–54.8. Their pose still attested active. The per-capture idle gate added after stop 1
   refuses the run on these alone. Who or what produced the input is not known here.
2. **The `UserNotificationCenter` modal alert returned at about 08:28:40Z and took focus.** It
   is the same process and window level as the alert first seen during the side's first launch
   after the grant, which was gone by 04:36Z. 183 captures up to 08:28:37Z attested active and
   all 23 from 08:28:46Z inactive, with none out of place. No HID input accompanied it: idle
   reads 1,073 s at 08:28:37Z. It is on screen and frontmost now (`stop-2/session-after-stop.json`,
   `stop-2/lsappinfo-unc.txt`). Its text is still unread, because reading it needs a permission
   this shell does not hold, and nothing has clicked it.

The orchestrator stopped at the refusal and committed it (`5a54f2cb`). Nothing was retried. The
opening and closing machine reads agree (mode 69, 0 foreign processes). This worker touched
nothing on screen.

**What the next continuation needs.** The alert is a system modal that appears unattended and
takes the active pose from the harness. While it is on screen, every later active capture is at
risk. A human has to read it and answer it: it may be a Screen Recording re-confirmation for the
side app, or something unrelated. Nobody clicks Allow on a permission prompt without the user
deciding. The continuation is then a fresh run 7 of active-1x, since the driver refuses to
overwrite anything, followed by active-2x and the rest in order.

**Both alerts identified, and the continuation after stop 2** (the parent's explicit, recorded
act). The `UserNotificationCenter` alert was a macOS **Files and Folders** prompt: "'2.1.283'
wants to access files in your Documents folder", with Don't Allow / Allow. `2.1.283` is the
Claude Code binary, so a process of this agent session touched `~/Documents`. It is **not** a
capture permission and has nothing to do with either harness bundle. The alert seen during the
side's first launch after the grant (step 3) was the same prompt. That is also the most likely
reason the side attested inactive on that launch. The parent answered it **허용 안 함 (Don't
Allow)** through System Events. The parent's message gives the time as about 08:50Z, but this
worker's session read at 08:34Z already showed the alert gone, so the answer came before 08:34Z. It was given with no keyboard or mouse input (HID
idle stayed above 20 min). The recorded denial stops it recurring for that binary. The HID input
at 08:10:44Z coincides with the user sending a message to this session and is treated as the user
typing on this machine; the user has been told to use the other machine. At continuation: Finder
frontmost, no Chrome, no alert, census 0 (`stop-2/session-at-continuation.json`). The pass order
continues with a **fresh active-1x run 7** (the quarantined run 7 keeps its name), then
active-2x, inactive-1x, inactive-2x and the sentinels. `tools/sitting-orchestrate.sh` gained an
optional first-run field for exactly this: the driver refuses to reuse an existing `run-N`, so a
continuation names the run it starts at.

## The sitting, complete (`sitting.json`, `attest/`)

**6,360 admitted captures**, first 03:09:53Z and last 21:50:42Z on 2026-09-26. That is the
declared baseline exactly:

| Pass | Mode | Runs admitted | Captures | Quarantined |
| --- | --- | --- | --- | --- |
| preflight-1x / 2x | 69 / 68 | 2 / 2 | 20 / 20 | — |
| active-1x | 69 | 7 | 1,568 | run 1 (stop 1), run 7 (stop 2) |
| active-2x | 68 | 7 | 1,568 | — |
| inactive-1x | 69 | 7 | 1,568 | — |
| inactive-2x | 68 | 7 | 1,568 | — |
| four sentinel passes (long protocol, settle 8 s, seed 3901) | 69/68/69/68 | 3 each | 12 each | — |

Every admitted run passed the corrected gates: per-capture HID idle of at least 60 s, the
by-name census, pose, window-frame and supplied-path attestations, and agreeing opening and
closing reads. The closing machine read (`attest/machine-close.json`) passes the 2x gates, with
mode 68 and 0 foreign processes.

## Step 6 — the archive of record (`archive/`, `bar/`)

- **Produced before plurality.** `archive-producer.py` ran over the 28 bed runs and then the 12
  sentinel runs, in sitting order (`archive/archive-producer-args.txt`). It archived
  **1,328 cells in 2,656 entries**: calibration 1,040, validation 144, holdout 144. It covers
  40 source manifests, with losing states kept and every dependency frame included. Of the
  1,440 declared cells, **112 are uncaptured, exactly the 56 phase-variant scenes × 2 profiles**
  the verdict did not admit. Inventory SHA-256 `58329732…35f61` (`archive/inventory.json`).
- **Published.** `release-asset.py` packed it to
  `w39-archive-489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5.tar.zst`:
  **13,658,148 bytes**, SHA-256 **`489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5`**.
  It is published as GitHub release **`w39-archive`** ("W39 repeat archive") on
  `SSFSKIM/designer`, created `--latest=false` and targeting `0cfbb325` (origin/main at
  publication). GitHub's own asset digest agrees (`archive/release-view.json`). It is the
  repository's only release, so GitHub lists it as "Latest" whatever the flag says; no npm
  release line is displaced (`archive/release-list.txt`). The archive is **not** in Git.
- **Round-tripped.** `fetch-archive.py --tag w39-archive --asset … --sha256 …` downloaded it into
  `~/.cache/vitrea-archives/489db938…/`, verified the full digest before extraction, extracted it
  and re-checked the tree against its inventory (`archive/fetch-verified.json`). The fetched tree
  is byte-identical to the producer's output.
- **Replayed with the whole W39 tree denied.** `replay-archive.py` ran from the main checkout,
  whose instrument files are byte-identical to this branch's, with
  `--deny-raw-root /Users/new/vitrea-w39`. That forbids the raw runs, this worktree and the
  producer's output alike. It recomputed **all 1,184 calibration and validation cells:
  identical** (`archive/replay-archive.json`).
- **Second owner-controlled copy.** `~/vitrea-w39/archive-copy/`, verified and extracted through
  `fetch-archive.py --source`; its tree is identical to the downloaded one
  (`archive/second-copy.txt`).

**The bar** (`tools/report-bars.py`, run on the fetched archive with the raw root denied;
`bar/bar.json.gz` and `bar/sentinel-bar.json.gz` hold every cell, member, bin and channel;
`bar/bar-headlines.json` has the headline, per-stratum max/median, and every bin above the
floor):

- **Normal protocol, seven runs:** 576 measured glass cells (calibration 504, validation 72).
  **575 of them are byte-identical across all seven runs**; one has two states (below).
  - **Deep bar: 0.5 in all 1,776 channel values, max = median = 0.5.**
  - **Edge bar: max 0.6, median 0.5.** 815,222 of 815,232 channel values sit at the 0.5 floor.
  - 47,936 bins are UNMEASURED by population, in every run alike.
  - Per stratum (1x/2x × light/dark): deep max 0.5 everywhere; edge max 0.6 (1x light), 0.5
    elsewhere.
  - The other 608 cal/val cells carry no bar by construction: 488 native-only references (456
    captured in run 1 only by declaration) and 120 opaque controls, read as coverage.
- **Long protocol (the sentinels), three runs:** 16 measured cells, 15 byte-identical; deep 0.5
  everywhere; edge max 0.528.
- **The one two-state cell:** `apple-macos-27.0-1x-light-standard-glass0.5/transfer-h210-colour__rest`
  (validation). Runs 1, 3, 4 and 7 hold one state and runs 2, 5 and 6 the other; the difference
  is sub-code (bar 0.5625 on a few 8-pixel arc bins).
- The spatial deep min/max is recorded per cell beside its bar, never as noise.
- **The holdout's bars are not computed.** Its payload stays behind the procedural boundary for
  G2's once-only exposure, which can derive them from the archive.

## Step 7 — the materialised probe bed (`probe/`, `wave-plan.json`)

`tools/materialize-probe.py --root ~/vitrea-w39/run --archive-inventory ~/vitrea-w39/archive/inventory.json`
wrote **1,328 cells by identification role**: calibration 1,040, validation 144, holdout 144.
Probe inventory SHA-256 `b164a79f…797c`.

- 823 cells were resolved by `materialize.ts` over runs 2–7 with run 1 folded in; run 1 agreed
  on **all 823** (0 differ).
- 504 run-1-only colour references were added from run 1, marked `singleRun`.
- **1 cell was decided over all seven runs.** The first attempt refused, which is what the tool
  did before this change: `materialize.ts`, given runs 2–7, found no plurality on
  `transfer-h210-colour` 1x light, a 3–3 tie within raster precision. Run 1, the seventh vote a
  seven-run `materialize.ts` would have counted, breaks it 4–3. The tool now hands such a cell to
  `materialize.ts`'s own `--omit` and publishes it at the plurality of all runs, recording
  `pluralityOfAllRuns` on the entry. No strict plurality over all runs still refuses. This is
  tested end to end (`tools/test-g1-tools.py`, 7/7). The refused attempt's logs are at
  `~/vitrea-w39/probe-FAILED-attempt-1/`.
- Holdout public manifest entries carry inventory and admission fields only. The full staged
  manifest and the materialiser logs are under `probe/holdout/`, and the guarded reader refuses a
  holdout read without the receipt (checked).

`wave.py plan --roles calibration,validation` is committed as the G2 hand-off
(`wave-plan.json`): **138 scenes selected, 214 excluded** (180 native-only controls, 6 off-centre
placements, 4 columns, 24 fractional sizes), the counts G0 recorded. **Nothing was executed
against vitrea.** `--execute` was not passed, and no browser, no compare and no web capture ran
in G1.

## Step 8 — ledger and close checks

The ledger entry is **c9a §5.185**, at the end of `docs/doperpowers/specs/c9a-fidelity-claims.md`.
Close checks:
- freeze **1,818 intact** (`freeze-verify-close.txt`);
- the seven W39 Python suites pass (`python-suites-close.txt`);
- the calibration suite passes 58 files, 761 tests with one skip (`calibration-test-close.txt`);
- calibration lint and every TypeScript check pass (`calibration-lint-close.txt`).

The original bundle's grant is **not restored**; Decision Log 4 does that at wave close. The side
bundle holds the machine's only vitrea Screen Recording grant. The raw run root, the archive
directory, the release staging directory and the second copy all stay on the capture machine
under `~/vitrea-w39/`.

## Wave close (2026-09-27)

The original bundle's grant was restored and checked at wave close; see `wave-close/README.md`.
