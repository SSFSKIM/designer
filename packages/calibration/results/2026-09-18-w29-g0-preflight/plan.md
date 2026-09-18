# The 27 bed's passes — priced on 27, from G0's own captures

W29 G0 (f). `pass-plan.py` derives the table from `apps/reference-apple/scenes.json` and the
committed manifest; the seconds per cell are `timing.py`'s reading over the 22 attested scratch runs
this gate took.

## Seconds per cell, measured

| reading | value | from |
| --- | --- | --- |
| dwell per cell (first `capturedAt` to last, over cells − 1) | **10.08 s** mean, 9.00–11.00 | 22 runs |
| wall per run | `0.4 s + 10.09 s x cells` | a two-point fit over the 2-cell and 6-cell runs |

The 26.5 record prices a cell at **9.5 s**; 27 costs **10.09 s**, about **6 % more**. The launch,
the window presentation and the manifest write together are under half a second, so a pass is
priced on cells and not on runs. Every run above carried `--reset-interstitial 6`, the sitting's
own setting; nothing here is priced at a different protocol from the one G1 will run.

## The passes

A pass is one scale, one accessibility mode and one pose — the unit `run-sitting.sh` takes, because
the accessibility mode is a read-only environment value set in System Settings and the pose is a
launch-time property of the process. Seven runs, the bar clause 2 declares.

| pass (scale x a11y x pose) | profiles | declared cells | 26.5 published | one run | seven runs | with 1.3–2.5x attempt loss |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 2x x standard x active | 2x-dark-standard, 2x-light-standard | 162 | 161 | 27.2 min | 3.18 h | 4.13–7.95 h |
| 2x x standard x inactive | 2x-dark-standard, 2x-light-standard | 119 | 117 | 20.0 min | 2.33 h | 3.04–5.84 h |
| 1x x standard x active | 1x-dark-standard, 1x-light-standard | 162 | 162 | 27.2 min | 3.18 h | 4.13–7.95 h |
| 1x x standard x inactive | 1x-dark-standard, 1x-light-standard | 119 | 117 | 20.0 min | 2.33 h | 3.04–5.84 h |
| 1x x increased-contrast x active | 1x-light-increased-contrast | 10 | 10 | 1.7 min | 0.20 h | 0.26–0.49 h |
| 1x x increased-contrast x inactive | 1x-light-increased-contrast | 22 | 22 | 3.7 min | 0.43 h | 0.56–1.08 h |
| 1x x reduced-transparency x active | 1x-light-reduced-transparency | 9 | 9 | 1.5 min | 0.18 h | 0.23–0.44 h |
| 1x x reduced-transparency x inactive | 1x-light-reduced-transparency | 21 | 21 | 3.5 min | 0.41 h | 0.54–1.03 h |

**8 passes, 624 declared cells**, of which 619 were ever published on 26.5. The five the
declaration carries and the 26.5 bed never published are named here so G2 does not meet them as
absences in a diff (`declared-not-published.py`); all five are on a dark-standard profile:

```
apple-macos-26.5-1x-dark-standard/light-solid__capsule-button__inactive
apple-macos-26.5-1x-dark-standard/photo__glass-over-glass__inactive
apple-macos-26.5-2x-dark-standard/checkerboard-8__capsule-button__rest
apple-macos-26.5-2x-dark-standard/light-solid__capsule-button__inactive
apple-macos-26.5-2x-dark-standard/photo__glass-over-glass__inactive
```

The first of those, `light-solid__capsule-button__inactive` on the two dark profiles, is the scene
§5.148 §1 already found the publishing run passing over with no committed native fixture. A 27 pass
will attempt all five; whether any of them files is a finding for G1's `sitting.md`, and a 27 cell
with no 26.5 counterpart is a cell G2 reports rather than diffs.

- one round over every pass: **104.9 min**
- seven runs: **12.24 h**
- with the W27 record's 1.3–2.5x attempt loss: **15.9–30.6 h**

The charter's estimate was 15–29 h from the 26.5 second-per-cell; the measured figure moves it by
about an hour at each end. These are hours of machine unavailability, not of work: the idle gate
means the machine must be untouched, and X7 forbids a browser suite beside it.

## The order to run them in

**Standard first, both scales, both poses** — four passes, 11.02 h at the bar, 14.3–27.6 h with
attempt loss. They are the four profiles every fidelity claim is fitted on, and they need no hand
on System Settings. The two 1x passes need the BetterDisplay screen switched to displayplacer mode
69 and back to 68 afterwards; both modes are present and both were reached and left in this gate
(`machine.json`).

**Then the two accessibility modes**, four small passes, 1.22 h at the bar, 1.6–3.0 h with attempt
loss. Both need the user's hand in System Settings > Accessibility > Display, and the harness
refuses a profile whose key claims a mode the machine is not in, so a wrong toggle costs the pass
rather than mislabelling a fixture. On 26.5 macOS force-coupled Reduce transparency on with
Increase contrast; whether 27 still does is not read here and G1 must record whatever it finds.

## What G1 has to carry that the W27 script does not

1. **The version gate inverts.** `run-sitting.sh:50` refuses anything that is not `26.5*`. The 27
   script refuses anything that is not `27.0*`.
2. **The slider is an axis and it is not attested by the harness.** G0 (d) measured that
   `NSGlassTintAmount` moves every cell of every arm, in both poses and at both scales, far beyond
   the cell's own run-to-run spread. Nothing in the manifest records it. Until the harness reads
   it, a pass must read and record the key itself — and X2's bar is that an attestation is a read
   that can **refuse**, which a shell `defaults read` beside the run is not. The harness change is
   one line in `Manifest.swift`'s hardware block plus a refusal, and it does **not** need the
   granted bundle rebuilt if the refusal is put in `materialize` instead (X4, Design).
3. **The machine is not at the centre.** It reads 0.5459057; the centre is 0.5 (G0 (d)). The
   difference is above the noise bar on all ten probe cells. Decision Log 3 has to rule what the
   bed is captured at before a pass runs.
4. **`hardware.sdk` is an environment field and reads `unknown` through the pass's own launch.**
   `capture.sh` derives `VITREA_SDK` from the installed SDK and exports it; `run-sitting.sh`
   launches the bundle through `open` without it, so every manifest this gate wrote reads
   `"sdk": "unknown"` and `"xcodeVersion": "unknown"`. X2 asks for the **capturing bundle's linked
   SDK, read from the binary**. That is `LC_BUILD_VERSION`'s `sdk` field from `vtool`, and on this
   build path it is not the SDK that compiled the binary — see `sdk-gating.json`. G1 should record
   both: the field as read from the binary, and the SDK path the build used, named as a build fact
   rather than a binary read.
5. **The granted bundle is older than `HEAD`.** Its binary predates `ee9e7449`, so it has no
   `dump-layers --inactive`. That commit touched `dump-layers` and `build.sh` only — the capture
   path is identical — so the bundle is still the right one to capture with, and X4 still says do
   not rebuild it. Anything needing the newer dump path uses a `VITREA_BUILD_OUT` side build, as
   this gate did.
6. **`dump-layers --inactive` cannot name a declared inactive id.** `refuseScenesUnreachableInPose`
   is called with `pose: .active` before `--inactive` is read, so every `__inactive` id is refused
   whatever pose the run is about to present in. The recede is a property of the presentation, so a
   `rest` id under `--inactive` is the same reading; the ordering is a harness bug and belongs in
   the tracker rather than in a pass's way.
7. **A run that loses the pose mid-pass looks like a material difference.** One of this gate's 24
   runs did: `active-1x/0.5-r3` recorded `presentedActive: false` at 4–14 s of HID idle, and
   against its neighbours it read maxDelta 99 and ΔE 0.183 — the size of the slider's whole range.
   `run-sitting.sh`'s audit catches exactly this and quarantines the run; `audit-runs.py` beside
   this file is the same rule for a probe. The run is kept under `QUARANTINE-` in the scratch tree.
