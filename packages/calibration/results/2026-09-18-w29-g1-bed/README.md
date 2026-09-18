# W29 G1 — the macOS 27 bed, 2026-09-18

The claims section is **c9a §5.150**; the charter is
`docs/doperpowers/specs/2026-09-16-w29-os27-recapture.md`, child G1. This directory is Part A: the
bed's infrastructure, proven against the real machine and the real granted bundle, with **no 27
fixture filed**. Part B materialises the fixtures from the banked runs and is dispatched after the
parent has run the sitting.

Raw captures stay on the machine — the SDK-pixel arm under `~/vitrea-w29-g0-scratch/sdk-pixel/`, the
sitting's runs under `~/vitrea-w29-27-run/`. What is here is derived: the runbook, the records and
every script that produced them.

| file | what it is |
| --- | --- |
| `commands.txt` | the eight passes' exact command lines, apart from the runbook's prose |
| `RUNBOOK.md` | the operator's document: the pre-flight, the exact command for each of the eight passes, what "done" looks like, and every refusal and what it means |
| `run-sitting-27.sh` | one pass of the bed. The version gate on 27.0/26A428, the slider, Show Borders, the accessibility mode, the display's mode and the capturing binary's linked SDK read and refused before pixels; a closing re-read diffed against the opening one; the W27 per-cell pose audit and quarantine, with run-level checks read out of the manifest the harness itself wrote |
| `run-sitting-27.test.sh` | 27 rows over that script's refusals and control flow, machine stubbed. The half a rehearsal on a correctly-configured machine cannot reach |
| `pass-spec.py` | the 27-only scene specification a pass reads, derived from the canonical declaration at every pass's opening, and the pass's cell list per pose and mode |
| `rehearse-all.sh` | the four standard `DRY=1` rehearsals in one go, switching the display for the 1x arms and returning it to mode 68 |
| `logs/rehearsal.txt` | what those rehearsals printed: 119 / 162 / 119 / 162 cells, 1 h 02 m, all clean |
| `attest/` | the four rehearsed passes' opening and closing attestation reads, as the runbook asks a real pass's to be committed |
| `plan.md`, `price-passes.py` | the eight passes re-priced off the committed 27 keys: 624 declared cells, 12.25 h at the seven-run bar, 15.9–30.6 h with attempt loss |
| `bar-table.md`, `verify-bar-table.py` | clause 2's 26.5 bar per cell, independently re-derived and **confirming G0's on every figure** |
| `sdk-pixel.json`, `sheets/sdk-pixel.png`, `harness-pixel-arm.sh`, `sdk-pixel-pairs.sh`, `sdk-pixel-sheet.py`, `audit.txt` | the harness half of the SDK-gating pixel arm, and the verdict: byte-identical, which closes G0's residual |
| `verify-output.txt` | the freeze verify, the lint and the test run, recorded at the commit |
| `freeze-verify.txt` | the 26.5 freeze, re-verified after every capture this gate took |

## What changed outside this directory

- **`apps/reference-apple/scenes.json` → version 6.** Six 27 profile entries beside the six 26.5
  ones, keyed `apple-macos-27.0-…-glass0.5`, declaring the **same scenes in the same split**. A diff
  against version 5 is six profile entries and one `$comment-version-6`; no scene, background,
  component, tint or split membership moves.
- **`packages/calibration/src/profile.ts`.** `PROFILE_KEY_PATTERN` gains an optional trailing
  `-glass<amount>` token and `NativeProfile` an optional `glass`. A 26.5 key parses exactly as it
  did, with **no** `glass` property — the axis is absent before 27, not unspecified.
- **`packages/calibration/src/run-provenance.ts`** (new, exported from the barrel) and its use in
  **`cli/materialize.ts`**: before a single PNG is opened, whether these runs were taken on the
  machine their profile keys describe, and whether they were all taken on the same one.
- **Tests.** `profile-key.test.ts` (the grammar, both beds), `run-provenance.test.ts` (both
  refusals), `scene-matrix.test.ts` (a `W29's macOS 27 bed` block, and the existing per-bed
  assertions widened to hold of both beds rather than accidentally excluding the new one).

## The three findings

**1. The key's slider token is last, and that placement is a grammar rule rather than a
convention.** Decision Log 3 (a) and the charter's Design put it last; what makes it *safe* is that
the granted bundle reads exactly one thing out of a profile key — the substring `-<scale>x-` — and
takes the colour scheme and the accessibility mode from the profile's own declared fields. So the
bundle accepts either placement without a rebuild (X4) and the decision falls to the readers that do
parse positionally. Appending after the a11y mode leaves every earlier axis at the offset a 26.5 key
has it at; a mid-key spelling would move the scale and scheme tokens and silently change what
`profile.key.includes("-2x-")`-shaped and `endsWith("-standard")`-shaped code selects. The rehearsal
is the proof rather than the reasoning: the granted harness parses version 6 and presents all four
standard passes' cells under the new keys.

**2. A pass cannot read the canonical declaration.** The harness selects profiles by accessibility
mode and display scale and by nothing else — it has no profile filter, and `--scenes` narrows cells
rather than profiles. With both beds in one file, a 2x standard pass would select **four** profiles
and spend twice the priced hours writing 27 pixels into `apple-macos-26.5-…` directories inside the
run snapshot. `pass-spec.py` derives a 27-only specification at the opening of every pass and
refuses unless the canonical file still declares exactly the six keys clause 2 names, each at the
ruled position, each carrying its 26.5 counterpart's scenes.

**3. The SDK-gating pixel arm closes G0's residual, and the side arm's third run is not evidence.**
Byte-identical on every attested cell pair, at zero run-to-run spread in both arms — see
`sdk-pixel.json`. Separately, G1's audit of the banked side arm found `active-r3` attesting 3 of 8
cells: five lost the presentation pose at 1–5 s of HID idle, and a sixth attested the pose at 0.1 s
of idle. Its two undisturbed cells are byte-identical to the harness arm. Every disagreement in the
whole comparison is accounted for by a run's own record of being disturbed, and none by the bundle.

## One count the dispatch and the charter disagree on

The dispatch asked for **eight** 27 profile entries; the charter's clause 2 enumerates **six**
(`{1x,2x}×{light,dark}-standard` plus the two 1x light accessibility keys), and six is what is
committed. Eight is the number of **passes** — each scale × mode × pose — and a pose is not a
profile: an inactive pass captures the `__inactive` scenes these same six keys already declare.
`scene-matrix.test.ts` pins the six and says so.
