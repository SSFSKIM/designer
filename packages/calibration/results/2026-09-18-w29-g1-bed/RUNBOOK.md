# The macOS 27 bed — the sitting, pass by pass

**For whoever drives the capture machine.** W29 acceptance clause 2, Decision Log 3, claims §5.150.

This bed is the new reference. Every native pixel vitrea has ever been measured against was captured
on macOS 26.5.2, and from 2026-09-14 "Apple's material" is what a Mac on 27 draws. The 26.5 bed is
frozen evidence and nothing here writes near it (contract X1); the 27 bed is captured beside it,
under new keys, over the same scenes and the same split, so that G2 can read 27 against 26.5 cell by
cell.

**12.25 h of machine time at the seven-run bar, 15.9–30.6 h with the record's attempt loss, across
eight passes.** Those are hours the machine can do nothing else: the idle gate means it must be
untouched and contract X7 forbids a browser suite beside it. See `plan.md`.

---

## 1. Before you start

| check | how | why it stops the run |
| --- | --- | --- |
| **OS is 27.0, build 26A428** | `sw_vers` | `run-sitting-27.sh` refuses anything else, first and unconditionally. A point update is a different material and a Decision Log entry, not a continuation. |
| **Do not update** | turn off automatic updates before you begin | An update mid-sitting ends the bed: half its runs would be a different build, which `materialize` then refuses as a plurality across two materials. |
| **The appearance slider is at 0.5** | `defaults read -g NSGlassTintAmount` → `0.5`. If not: `defaults write -g NSGlassTintAmount -float 0.5` | Decision Log 3 (a) captures this bed at the system default. G0 measured the slider moving 10 of 10 probe cells beyond their own run-to-run spread, in both poses, at both scales, in both schemes — including at the machine's as-found 0.5459057, which is 0.046 off centre. The position is in the profile key (X6) and every run refuses unless the machine is at it. |
| **Show Borders OFF** | `defaults read com.apple.Accessibility ButtonShapesEnabled` → `0` | macOS 27 decouples it from Increase Contrast. It has no key in `com.apple.universalaccess` and no SDK property; the user's toggle against a 635-domain snapshot found it here (W29 Surprises). Off in every run of this bed; not an evidence class in this wave. |
| **Accessibility toggles OFF for the standard passes** | System Settings › Accessibility › Display: *Reduce transparency* off, *Increase contrast* off | The mode is part of a pass's identity and both the script and the harness refuse a pass whose declared mode the machine is not in, so a wrong toggle costs the pass rather than mislabelling a fixture. |
| **Display mode** | `displayplacer list \| grep 'current mode'` → **68** for a 2x pass, **69** for a 1x pass | The harness reads the real backing scale and SKIPS a profile whose key states another, so a pass at the wrong mode does not mislabel a fixture — it quietly captures the other scale's profiles into this pass's directory. The script refuses before pixels, and checks the manifest's own `actualBackingScale` afterwards. |
| **Screen Recording consent** | `cd /Users/new/Developer/GitHub/designer/apps/reference-apple && open -W --stdout /tmp/probe.log --stderr /tmp/probe.err build/VitreaReference.app --args probe && cat /tmp/probe.log` → must print `ScreenCaptureKit: OK` | **Launch through `open`, exactly as every pass does.** `./capture.sh probe` execs the same binary from your shell and macOS then charges the check to the *terminal application*, so it reports the terminal's grant and not the bundle's. `material rendered: NO` on the ImageRenderer line is that path's standing property, not a problem. |
| **Do not add any bundle to Screen Recording** | — | TCC keeps **one row per bundle identifier** and the last code hash added owns it. Adding the side bundle under the harness's identifier evicted the harness's grant on 2026-09-18 and cost a hand to restore (W29 Surprises; contract X4 now has a sharper reason). |
| **The granted bundle is not rebuilt** | — | A rebuild re-signs ad hoc, which is a new TCC identity and a lost grant. Experiments use `VITREA_BUILD_OUT` — into scratch, and **never** added to Screen Recording. |
| **Nothing else on the GPU** | close browsers, stop other agents' Playwright suites | The script refuses while a capture process is running and names what it found. |
| **Console session UNLOCKED** | no screen saver, no display sleep, no lock during the sitting | The harness refuses a locked screen outright, and the reason is measured: on a locked screen nothing can become active or key, so an active pass would capture the unfocused material under active ids and an inactive pass's attestation would pass for the wrong reason. The idle gate cannot catch it — a locked machine is maximally idle. |
| **Left alone** | no typing, no other GUI work; a Screen Sharing cursor over the shared screen counts | Each run refuses at its opening unless the machine has been idle 45 s, and the script waits 90 s and retries. **Per cell the harness records the idle and does not refuse**, so a touch mid-run files the cell with its `hidIdleSeconds` beside it; the run prints how many cells were captured under 45 s and `sitting.md` lists them. This is not academic: the side bundle's `active-r3` in the SDK-pixel arm lost the presentation pose on five cells at 1–5 s of idle and is not evidence (`sdk-pixel.json`). |

Nothing is built. The bed is captured with the **already granted** bundle at
`/Users/new/Developer/GitHub/designer/apps/reference-apple/build/VitreaReference.app`, in the main
checkout, and the pass reads the scene declaration from whichever checkout you point
`VITREA_SCENES` at.

---

## 2. Prove the path before spending the machine

Three checks, in this order. The first two need **no machine state at all** — no display, no GUI
session, not even an unlocked screen:

```bash
R=<repo>/packages/calibration/results/2026-09-18-w29-g1-bed
bash $R/run-sitting-27.test.sh                          # the script's refusals, machine stubbed
(cd <repo>/apps/reference-apple && ./capture.sh self-check)   # the pure capture rules
DRY=1 $R/run-sitting-27.sh inactive 2 standard          # the real path, presenting and attesting
```

The third presents and attests every cell of the pass and captures nothing. It exercises every
refusal the real pass has — this script's attestation gates, the fixture root, the backgrounds, the
scene resolution, the presentation and the per-cell pose attestation. Under `DRY=1` a bare run
number means **one** rehearsal rather than seven.

**Read the count, not the verdict.** `cells presented:` counts **cells**, not ids — the harness
prints one line per profile × scene, and the standard passes carry two profiles. So it must print
**162** for an active standard pass, **119** for an inactive one, **10** and **22** for increased
contrast, **9** and **21** for reduced transparency. (The `--scenes` id list is smaller for the
standard passes — 96 and 72 — because the light and dark profiles declare overlapping lists; the
script prints that number too, as `cells=N ids`.) A count *under* the cell count is the failure this
step exists to catch, and the script will not catch it for you: it treats any nonzero count as
success. Rehearse after each toggle change and each display switch.

`rehearse-all.sh` does the four standard rehearsals in one go, switching the display for the 1x arms
and returning it to mode 68.

---

## 3. The eight passes

`VITREA_SCENES` must point at the checkout whose `scenes.json` declares the 27 profiles (version
6). The granted bundle was compiled from the main checkout, so its `#filePath`-based root cannot see
an amended declaration in a worktree — the path is passed explicitly to both the `backgrounds`
resolver and the open-launched app, and the pass runs against the **27-only specification derived
from it** (see `pass-spec.py`: the harness selects profiles by accessibility mode and scale and by
nothing else, so a pass against the canonical file would select both beds and spend twice the
sitting writing 27 pixels into 26.5-keyed directories).

### Standard first — four passes, 11.03 h at the bar

```bash
R=<repo>/packages/calibration/results/2026-09-18-w29-g1-bed
export VITREA_SCENES=<repo>/apps/reference-apple/scenes.json

# (a) and (b) 2x, standard. Display at displayplacer mode 68 (the machine's usual state).
DRY=1 $R/run-sitting-27.sh active   2 standard        # must print: cells presented: 162
$R/run-sitting-27.sh active   2 standard              # 3.18 h at the bar
DRY=1 $R/run-sitting-27.sh inactive 2 standard        # must print: cells presented: 119
$R/run-sitting-27.sh inactive 2 standard              # 2.34 h

# Switch the screen to 1x, and confirm it.
displayplacer "id:7709FD0F-F423-4277-B0C8-7CA94F85723A res:2560x1440 hz:60 color_depth:4 \
  enabled:true origin:(0,0) degree:0 mode:69"
displayplacer list | grep 'current mode'              # must read: mode 69

# (c) and (d) 1x, standard.
DRY=1 $R/run-sitting-27.sh active   1 standard        # 162
$R/run-sitting-27.sh active   1 standard              # 3.18 h
DRY=1 $R/run-sitting-27.sh inactive 1 standard        # 119
$R/run-sitting-27.sh inactive 1 standard              # 2.34 h
```

### Then the four accessibility passes — 1.22 h at the bar, each needing a hand

The display stays at **mode 69**; both accessibility profiles are 1x light, as on 26.5.

```bash
# (e) and (f) 1x, increased contrast.
#     System Settings > Accessibility > Display > Increase contrast ON.
#     macOS force-couples Reduce transparency ON with it; that coupling is the only reachable
#     increased-contrast state and the harness records it as a profile caveat.
DRY=1 $R/run-sitting-27.sh active   1 increased-contrast   # must print: cells presented: 10
$R/run-sitting-27.sh active   1 increased-contrast
DRY=1 $R/run-sitting-27.sh inactive 1 increased-contrast   # 22
$R/run-sitting-27.sh inactive 1 increased-contrast

# (g) and (h) 1x, reduced transparency.
#     Increase contrast OFF, Reduce transparency ON.
DRY=1 $R/run-sitting-27.sh active   1 reduced-transparency # 9
$R/run-sitting-27.sh active   1 reduced-transparency
DRY=1 $R/run-sitting-27.sh inactive 1 reduced-transparency # 21
$R/run-sitting-27.sh inactive 1 reduced-transparency

# Toggles back off, and the display back to 2x.
displayplacer "id:7709FD0F-F423-4277-B0C8-7CA94F85723A res:2560x1440 hz:60 color_depth:4 \
  enabled:true origin:(0,0) degree:0 mode:68"
```

No `VITREA_SITTING_DIR` or `VITREA_BED_FILE` is needed for any of them, and that is the one thing
about the command shape that changed from W27. That script named a pass by pose and scale only, so
the accessibility passes resumed over the banked standard runs until they were given their own root
by hand, and their id list had to be hand-derived because the profile declares a subset. Here the
accessibility mode is part of the pass's identity, the run directory is
`$HOME/vitrea-w29-27-run/<mode>-<pose>-<scale>x/run-N`, and the id list is derived per pass from the
declaration.

### What "done" looks like

- Every pass prints `PASS <mode>-<pose>-<scale>x DONE`.
- Every run prints `attested N N` — the two numbers equal — and beside them `cells under 45s idle`
  and `idle unreadable`. Those two are **reports**: the harness gates idle once at a run's opening
  and records it per cell without refusing. List every such cell in `sitting.md`.
- Each run directory holds its own `manifest.json`, its `attest.read` (the opening state) and its
  `attest.close` (the closing re-read). The two are diffed and a disagreement quarantines the run —
  every axis the opening read gates is settable from a shell or a preference pane while a 27-minute
  run is in progress, and a slider moved mid-run puts cells at two positions under one key.
- `$HOME/vitrea-w29-27-run/` holds eight pass directories × seven run directories.

### The script resumes, and a tainted run does not look banked

A run whose `manifest.json` already exists is skipped, so an interrupted pass is restarted with the
same command. A run that FAILS — its per-cell audit, its run-level checks, or the attestation diff —
is quarantined under `QUARANTINE-run-N-<timestamp>/`, which carries no `manifest.json` under the run
name, so the same command re-takes it instead of stepping over it. **Keep the quarantined run: what
failed to attest is the finding.**

---

## 4. What must NOT be done

- **Do not point `VITREA_FIXTURES` at `apps/reference-apple/fixtures`.** A narrowed run republishes
  each profile it captures *wholesale*: it would delete every cell of that profile it did not
  capture, and the merge would strip `recoveredProvenance` from 121 entries and the three
  run-frequency fields from 102 more. Both `--inactive` and `--scenes` refuse a fixture root that
  already holds a `manifest.json`, and the script gives each run a fresh one, so this cannot happen
  by accident.
- **Do not write anywhere under `apple-macos-26.5-*`, `fixtures/backgrounds/`,
  `packages/calibration/profiles/` or `results/matrix.json`.** X1; the check is
  `python3 results/2026-09-16-w29-freeze/freeze.py verify`, which must print
  `26.5 freeze intact: 1762 entries`.
- **Do not treat this as a freeze-bar sitting.** Seven runs buy one bar per pass. No 27 regression
  floor comes out of it (clause 4) — a floor needs the seventeen-run bar, and `bar-table.md` records
  why the 26.5 bar cannot be matched per cell for 38 % of the bed.
- **Do not change the scene matrix, a material profile, a golden or the canonical matrix** during
  the sitting. The bed is declared; the sitting executes the declaration.
- **Do not fix up a cell that failed to attest.** Re-run the pass. A cell captured while something
  had activated the app is the one failure a recovered bed cannot rule out about itself.
- **Do not read any 27 fixture against vitrea.** That is G2 and then G3. This sitting captures.

---

## 5. If something refuses

| message | meaning |
| --- | --- |
| `REFUSED: macOS <v> is not 27.0` / `build <b> is not the declared 26A428` | The machine is not the bed's machine. Stop; report. |
| `REFUSED: NSGlassTintAmount reads '<v>', not the ruled 0.5` | `defaults write -g NSGlassTintAmount -float 0.5`. An **absent** key also refuses: the material renders at 0.5 without one, but a position inferred from an absence is not an attestation. |
| `REFUSED: this pass declares accessibility mode 'X' and the machine is in 'Y'` | Set the toggle in System Settings › Accessibility › Display. The mode is read-only to the process. |
| `REFUSED: Show Borders … reads '1', not 0` | Turn Show Borders off. |
| `REFUSED: the display is at mode N and a Mx pass needs mode M` | Switch it with `displayplacer` and re-run. |
| `REFUSED: displayplacer reported no current mode` | The BetterDisplay virtual screen is gone. Without it there is no 1x bed at all — four of the six keys. Stop; report. |
| `REFUSED: vtool read no LC_BUILD_VERSION` | The binary's linked-SDK record cannot be read, and X2 does not let it be guessed. |
| `REFUSED: a capture process is already running` | The GPU is shared; one at a time. |
| `REFUSED: the tint attestation would refuse a inactive bundle` | Inactive passes only. See the named rehearsal log. On an **active** pass this cannot fire — the active rule would report the committed bundle's recovered inactive cells and refuse every active pass, which is the W27 defect this script does not repeat. |
| `ScreenCaptureKit is unavailable … TCC` | Screen Recording is not granted to the process macOS holds responsible. From a pass (launched through `open`) that is the bundle: re-add its path in System Settings › Privacy & Security › Screen & System Audio Recording and confirm with the `open`-launched probe. |
| `the machine has been idle Ns, under the 45.0s this run requires` | Expected; the script waits 90 s and retries. Leave the machine alone. |
| `presentInactive: the window is … the application is ACTIVE` | The recede could not be reached before the first cell. Nothing was captured. Run `./capture.sh deactivate-probe`. |
| `scene '<id>': the inactive pose was lost before this cell` | Something activated the app mid-run. Nothing was published. Re-run the pass. |
| `N of the requested scenes declare a state this run's presentation pose cannot reproduce` | The id list and the pose disagree. The list is derived from the declaration per pass, so this means the declaration moved: run `pass-spec.py ids` by hand and report. |
| `Profiles not captured because this display renders at Nx` | Should not be reachable — the script refuses on the display mode first. If it fires, the mode-to-scale mapping in the script is wrong for this screen. Stop; report. |
| `the login session's screen is LOCKED` | Unlock the console session and disable display sleep. Nothing was captured. |
| `STOPPING: run N attested X of Y` / `RUN-LEVEL PROBLEMS` / `STATE DRIFTED` | A cell failed the four-part audit, or the run's own manifest disagrees with the pass, or the machine moved between the two attestation reads. The run is **quarantined**. Keep it and report the session state rather than spending the remaining runs. |

---

## 6. What to commit, and where

Not the raw runs — they are hundreds of megabytes of PNGs and the repository's practice is that a
sitting's raw snapshots stay on the capture machine, under `$HOME/vitrea-w29-27-run/`. Commit, under
this directory:

- **`sitting.md`** — when each pass ran, the wall-clock per pass, the attested counts per run, every
  retry and what caused it, every cell captured under 45 s of idle, the display and accessibility
  state per pass, and the OS build. Model it on `results/2026-09-11-w27-26.5-run/sitting.md`.
- **the per-run logs** (`run-*.out` / `run-*.err`) or a distilled digest, and every `attest.read` /
  `attest.close`.
- **`provenance.json`** — the run directories, their manifest hashes and their timestamps.

Publishing the bed into `apps/reference-apple/fixtures/apple-macos-27.0-*/` is `cli/materialize.ts`
at seven runs per pass, and it is **G1 Part B**, not this sitting's work: it is where the published
byte-state per cell is decided across the seven runs. `materialize` now refuses before it opens a
single PNG if a run's manifest or attestation disagrees with the profile keys it filed under, or if
the runs were taken on different OS builds (`src/run-provenance.ts`). Leave the raw runs in place
and report that they are banked.
