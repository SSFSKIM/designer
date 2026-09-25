# W39 colour-and-edge bed tooling

This is the pre-capture instrument for W39 charter clauses 1–10 and claims §5.184.
It declares the bed, not a measured W39 material. G1 must use the reviewed final bytes.

## Declaration and identities

Final `bounds-declaration.txt` SHA-256:
`94cebb42735a22f345b0a877ca5137d3355e84e78d09b12c9fabf67f0ba3faae`.

Declaration history is retained, not rewritten as if only the final version existed:

- **Corrected at the review (P1-1):** `6467da8560f0485c719eef76914b2728db1443d3f7c836fd9595ad51377432ba` is superseded
  by the final hash above. The amplitude optimizer's tolerance `1e-10` and cap `200` are
  now declared, with a finite-previous-RSS convergence guard. Earlier synthetic numbers
  are retained as initial readings; corrected synthetic results are recorded below.

- v1 `44d818b5d9df656e16c6801f66cb7faa60b41e19d472c06bb3fef44ea432fd18`,
  committed in `bf67d78d` before archive computations, used 36 preflight observations.
- Interim `b034470473e85e533bca8831946831b0e3dbf18d550699b61fd74235380e1683`
  added four phase-zero end-repeat observations and the integer-size near-band bound.
- Superseded `c47d8d6c8f92bc07e3c0327d517cee7664fe5610d4d1884c07c4b127356c10be` additionally compared a shared translated integrated profile against
  an equal-knot-count amplitude model, with rank, RSS and leave-one-phase-out requirements.
  The literal ramp stays diagnostic rather than rejecting a valid phase because of an
  exterior shadow or interior shoulder.
- Superseded `834f3cd29358a175f82f83c2e688e064552c9fb50e1956511a9e8f0b700d108a` uses one-device-pixel knots: synthetic analysis found an exact
  Nyquist null vector in the half-device grid under pixel-area integration. Held-phase
  tolerance adds the exact rounding propagation `0.5*||w_i||₁` to `max(0.5,D_int_far)`,
  reported per sample, not tuned to native residuals.
- The final declaration makes H2′ a five-parameter colour candidate per endpoint: retention
  plus four thin tone ordinates, thick held shipped. Span44's small thick contribution is
  fixed rather than introducing unidentifiable thick freedom; span64/96 transfer is tested
  and reported separately, never fitted. Shared thin/thick shifts are declined. All
  amendments precede any W39 native pixel.

`pins.json` independently binds the main scenes, the scene-level split, the separate preflight
scenes and the declaration. `closure.json` gives the numerical rules in machine-readable form.
`declare-bed.py` reproduces the scenes, split, twin audit and pins from `colour-cells.json` and
`edge-cells.json`; these input lists are the charter's grounding lists, not a tuning surface.
Run it only to reproduce an unchanged declaration, never to choose cells after capture.

The main file has 388 scene IDs: 40 edge + 63 colour + 63 run-1 references + two scale-specific
variants of 14 phase cells, each in both poses. Each profile admits only its scale's variants.
Every fixture role is `probe`. The identification split is 316 calibration / 36 validation /
36 holdout scene IDs, with whole glass/control pairs together; no canonical holdout twin was
found. The six held-out colours also own held-out no-glass references. Dependency role rank
is never above the dependent's; shared calibration controls are copied into a held-out role's
payload by the producer, not exposed to a reporting reader through that payload.

The g128 centre circular-120, red and green are W34 bridges: same relative geometry/backdrop,
**different 320×280 canvas**, not identical captures. Colour cells borrow the g128 centre
opaque registration, which measures ordinary fill, not glass raster coverage. Red and green
are explicit saturated bridge exceptions to the new 61-colour [40,150] box.

## Bundle and non-capturing checks

`bundle-pin.json` identifies the external, **ungranted** bundle at
`~/vitrea-w39/side/VitreaReference.app`. Its build-input revision is `25b268ec`; no Swift input
changed after that build. Never rebuild a granted bundle or use `capture.sh`'s auto-build path.
The worktree's compiled fallback root is not portable: always supply `VITREA_SCENES`,
`VITREA_FIXTURES` and `VITREA_SCALE` explicitly after merge as well.

`export-paths.swift` is a non-GUI exporter; its header gives the direct swiftc command.
`supplied-paths.json` and `preflight-supplied-paths.json` attest fractional sizes and centres
without rounding, including both independent column members. `native-test.txt` records the
native self-check. These supplied paths are not window-server raster-phase evidence.

`verify-backgrounds.py ~/vitrea-w39/backgrounds/backgrounds` checks the non-captured PNGs
emitted by the side binary's `backgrounds` command: 67 backgrounds × two scales, every solid
byte and every arithmetic gradient pixel exact. `backgrounds-verification.json` is the result.
These are generated sRGB rasters, not ScreenCaptureKit observations.

`tcc-read.json` is a read-only database observation: the system database records the original
`dev.vitrea.reference-apple` as authorised (`auth_value=2`), W34 as denied, and no W39 row.
The user database could not be opened and is explicitly not verified. Nothing here grants,
requests, scripts or restores Screen Recording permission. A prompt may appear at an
ungranted side bundle's first SCK call: **nobody clicks Allow**.

The parent observed a prompt naming `VitreaReference` around 02:00 KST on 2026-09-26. Its client
is **unattributed**. G0's `backgrounds` and `self-check` paths do not invoke ScreenCaptureKit;
no G0 capture launch had occurred when it was observed. The parent reports that the companion attempt was refused because screenshot access to
the TCC prompt was denied; it clicked nothing and changed nothing. The parent reports the user's hand dismissed it with Deny at **2026-09-25T17:16Z
(02:16 KST, 2026-09-26)**, and the window is gone. The parent's read-only system TCC query
found no new client row in the prior30 minutes and still no W39 row; the user database
remains unreadable. Either the prompt was stale after its requester exited or the answer
landed in that unreadable database; neither is established. No client attribution or
permission change is inferred. The saved rehearsal reads predate this dismissal; foreign
capture-process exclusivity is the remaining rehearsal blocker, with the matching display
mode to be set/read for each pass.

## Pass plan and sitting

Set `E` to this directory in the accepted checkout. All raw roots stay outside the repository.
`pass-spec.py plan` reproduces `pass-plan.json`. `derive(pose,scale,run,reachable_axes,sentinel)`
selects the exact scenes, not an opaque `--set probe` sweep. The plan charges:

- normal bed: 5,768 captures;
- run-1-only colour references: 504;
- three long runs on two sentinels per scheme/pass: 48;
- preflight: 40 (36 geometry captures plus four phase-zero end repeats);
- baseline total: **6,360**, 16.995 hours at 9.62 s/capture;
- one reachable axis adds 448; both add 784, for **7,144**, 19.090 hours.

The charter-v2 figure 6,356 used 36 preflight captures; the four additional drift controls are
an explicit pre-capture G0 amendment, not a silently changed count. Machine/mode/grant changes
and independent HID-idle preparation are outside the time estimate.

`run-sitting-w39.sh` / `sitting.py` derive from W34's refusal/attestation driver. They check
27.0/26A428, RT0/IC0/Show Borders0/tint0.5, display identity/mode, the pin including
LC_BUILD_VERSION, independent ≥60 s HID idle and unlocked state, zero foreign capture
processes, and opening/closing agreement. Failed attempts are retained/quarantined, never
retried in place. Each captured fixture must include supplied paths and requested/actual
window frames; these frames are an attestation, not a placement actuator.

For a strict refusal rehearsal (only after the machine is exclusive and the prompt is gone):

```bash
VITREA_SITTING_DIR="$HOME/vitrea-w39/rehearsal" \
  bash "$E/run-sitting-w39.sh" active 2 --rehearse-refusal
```

Repeat with active1, inactive1 and inactive2 at the matching attested display mode, each in
its own preserved pass directory. Do not use `DRY=1`, which the new driver refuses. A failed
attempt is not automatically retried; preserve the quarantine and use a fresh declared root.
The compiled non-GUI `read-session.swift` reader defaults to
`~/vitrea-w39/scratch/read-session`; it reads independent HID idle, lock state and on-screen
window owners, including an outstanding permission prompt, before any launch.

A rehearsal writes `run-1/rehearsal.json` with one outcome. `refused-tcc` is the only one
admitted: the capture was attempted (the harness printed its `capturing N fixtures via
screencapturekit` line), `producer-capture.err` carries the harness's own TCC-gate sentence,
and no manifest, fixture PNG or staging directory remains. `captured` means the ungranted
side published pixels, so it holds a grant it must not hold; stop, and do not use those pixels.
`prompt-pending` means the launch hung past 180 s, or a window owner appeared that outlived
it, or a `universalAccessAuthWarn` window is on screen afterwards. `refused-other` is any
other refusal. The last three are quarantined with `refusal.txt`. If macOS prompts for
`dev.vitrea.reference-apple.w39` during a rehearsal, **nobody clicks Allow**. G1's grant then
follows the harness README's remove-and-re-add recipe, because a recorded denial suppresses
the prompt, and that is the planned path anyway. An opening refusal names every failing gate
in one message, and its `attest.open.json` and `session-before.json` are always kept.

The preflight is two sitting passes per scale. Run 1 captures the nine geometries x
glass/opaque (18 captures); run 2 is the phase-zero pair repeated at the END. Then one scoring step freezes the verdict:

```bash
VITREA_SITTING_DIR="$HOME/vitrea-w39/run" python3.12 "$E/preflight.py" run 1   # mode 69
VITREA_SITTING_DIR="$HOME/vitrea-w39/run" python3.12 "$E/preflight.py" run 2   # mode 68
python3.12 "$E/preflight.py" verdict --root "$HOME/vitrea-w39/run"
```

`preflight-verdict.json` is written once, beside the passes. It records every number per
scale and axis: opaque byte states, D_int_near/D_int_far, the SHIFT and AMPLITUDE fits,
rank and condition number, and each held-out phase's residual with 0.5·‖w_i‖₁ per sample. It
also records the axis statuses (`reachable`, `unreachable`, `not-identified`,
`UNMEASURED-drift`), the branch and the admitted phase scenes. The first bed pass pins the
verdict's SHA-256 in `verdict-pin.json` and refuses a changed verdict. It also re-derives
the admitted scenes from `pass-spec.py` and refuses a disagreement. `test-preflight.txt` is
the synthetic-bed record the knot spacing and the LOPO tolerance were ruled on. No native
pixel is read there.

The preflight precedes all bed passes. Only axes admitted by its frozen verdict enter the
seven-run bed; phase variants belong to exactly the tested fractional-size actuator. The
phase-zero end sentinel detects temporal drift separately from a failed actuator. There is
no fallback actuator or inference of edge phase from backdrop motion. After preflight, pass
order is active-1x, active-2x, inactive-1x, inactive-2x; long sentinels stay separate from normal
runs and their bars. Two schemes share a GUI process.

A dry rehearsal means an **attempted real SCK capture expected to be refused, with no manifest**,
not the harness's `--dry-run` presentation-only path. The unrelated Playwright/Chrome session
observed on the machine prevents exclusivity; it is not terminated by this gate. Opening
refusals under `dry-attestations/` are not TCC-refusal evidence. All four saved opening
reads show 14 foreign capture processes and the outstanding permission prompt; 1x also saw
mode68 instead of69. The first validator additionally miscompared a trailing newline in
`LC_BUILD_VERSION`; its regression-tested fix normalises surrounding whitespace, and
`reevaluated-gates.json` proves the saved reads match the unchanged bundle pin. Original
refusals are retained verbatim; this re-evaluation launches nothing. A TCC-level rehearsal remains
outstanding: retry before merge only if the machine is genuinely exclusive; otherwise it is
the first G1 runbook step while the side is still ungranted, **before the grant switch**.
The parent's grant-switch runbook, not this G0 tool invocation, owns that user action.

## Archive and body/edge readers

`archive-exclusions.py` re-reads only W34 calibration and explicitly labelled validation
through its guarded reader. `archive-exclusions.json` records H1 and shipped-H2 exclusions;
W34's spent holdout and sealed bulk are never inputs. `w39_readers.py` reads attested origins,
continuous supplied paths, circular stadiums and independent column members, shells to −14
CSS inward / +4 outward, equal-depth side pairs and separately calibrated opaque coverage.
`test-w39-readers.py` reproduces the W37 calibration witnesses, not W39 holdout pixels.
The declaration's “W37 X13” arc-bin citation is a clerical mis-citation: the numerical
authority is W37 `identify.py`'s 16 nearest-normal bins of 22.5°, not its identity-table X13.
The archive-exclusion reading retains its recorded interim declaration hash `b0344704…`;
`archive-exclusions.py --verify` reproduces it under the final preflight-only amendment and
reports both hashes. No recorded hash or measurement is rewritten to pretend a later origin.

`archive-producer.py` takes every admitted normal and long run in sitting order. It copies
complete lossless glass/no-glass/opaque frames with metadata and per-run provenance into
role-separated payloads, including losing states. Missing run-2+ colour references and long
sentinel dependencies resolve to the matching first normal run and keep its input hashes.
Do not include preflight or quarantined runs. For example, construct the complete argument
list rather than publishing a hand-picked subset:

```bash
RUN="$HOME/vitrea-w39/run"
args=()
for pass in active-1x active-2x inactive-1x inactive-2x; do
  for n in 1 2 3 4 5 6 7; do args+=(--run "$RUN/$pass/run-$n"); done
done
for pass in active-1x active-2x inactive-1x inactive-2x; do
  for n in 1 2 3; do args+=(--run "$RUN/$pass-sentinel/run-$n"); done
done
python3.12 "$E/archive-producer.py" "${args[@]}" --out "$HOME/vitrea-w39/archive"
python3.12 "$E/release-asset.py" pack "$HOME/vitrea-w39/archive" \
  --out-dir "$HOME/vitrea-w39/release"
```

The packer verifies the inventory before creating a deterministic `.tar.zst` under 2 GiB,
`w39-archive-<64-hex SHA-256>.tar.zst`; the digest names the tarball, not a directory. It prints
the exact `gh release create w39-archive … --latest=false` / `gh release upload` commands for
G1, including a target-revision placeholder G1 must fill. No release is created in G0.
The publication ledger must cite tag, asset, full digest, byte size and replay command. Keep a
second owner-controlled copy outside the repository; a hash detects replacement, not loss.

```bash
ROOT=$(python3.12 "$E/fetch-archive.py" --tag w39-archive \
  --asset "w39-archive-$SHA.tar.zst" --sha256 "$SHA")
python3.12 "$E/replay-archive.py" "$ROOT" --deny-raw-root "$HOME/vitrea-w39/run"
```

The fetcher uses `~/.cache/vitrea-archives/<sha>/`, verifies before extraction, rejects unsafe
members and rechecks a reused cache. `--source <local tarball>` exercises the same verified
path on the owner's second copy without a network download. Replay recalculates the actual
instrument outputs with raw reads denied, rather than comparing stored summaries.

`wave.py plan` defaults to calibration and validation. It explicitly excludes native controls
and every unsupported web placement: off-centre shapes, columns and fractional-size phases.
These remain native identification evidence, with their dependencies, not misplaced web
comparisons. Extending `component-region.ts` for position/column is Deferred outside G0.

```bash
python3.12 "$E/wave.py" plan --fixtures "$HOME/vitrea-w39/probe" \
  --out-matrix "$HOME/vitrea-w39/matrix.json" --captures "$HOME/vitrea-w39/web-captures"
```

The present plan selects 138 scene IDs; 214 are excluded with reasons (180 controls, six
off-centre placements, four columns, 24 fractional-size variants). Holdout is never allowed
without `wave.py expose`: the receipt binds candidate, runner, instrument, closure and exact
archive inventories; its runner receives `W39_WAVE` / `W39_AUTHORIZATION`. A failed exposure
is spent. W39's procedural boundary is not permission to revisit W34's spent holdout.

## Verification

Use `python3.12` for numpy/PIL. The workspace install and recursive build ran before tests.
`w39-scenes.test.ts` validates profiles, roles, pairings, colour bounds, placement, preflight
geometry and independent pins, and invokes the Python boundary/numerical suites when those
runtime dependencies are present. Each `test-*.txt` records its direct invocation; the full
calibration suite and lint have their own logs. `freeze-verify.txt` must remain 1,818 entries.
Independent correctness review is the parent's next gate; these implementation checks do not
replace it. No W39 native pixel, measured repeat bar, preflight reachability or closing law is
claimed by G0.

Final checks: calibration54 files /718 passed /1 skipped; the seven W39 Python suites
pass71 tests in total (including the7 synthetic preflight tests); calibration lint and all
TypeScript checks pass; final freeze1,818 intact. `archive-exclusions-verify-final.txt` and
`test-declaration-final.txt` name the final declaration. The native frame-recording path
remains operationally unexercised and the TCC-level refusal rehearsal is still outstanding.
