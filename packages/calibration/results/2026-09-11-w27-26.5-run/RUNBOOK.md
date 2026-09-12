# The macOS 26.5 run — W27c G1b's checking bed and W27e's labelled probe

**For the user, on the capture machine. Written 2026-09-11.**

macOS 27 ships **2026-09-14**. A machine that has updated can never produce 26.5 evidence again,
and the frozen inactive endpoint of claims §5.130 was fitted against 26.5 — so a check of it taken
against 27's pixels would confound the recede with the version change and could not be attributed
to either (§5.134 §5, *the two paths*). This session is the last chance to take it.

W27 Decision Log 13 takes **both gates' runs at the probe bar**: the labelled vibrancy probe, and
the inactive checking bed at **7 runs**, not the freeze bar's 17. Consequences of the probe bar, so
they are not rediscovered later: **no inactive regression floor is adopted from this run**, W27c G3
stays a later gate, and the whole bed is declared `probe` in `scenes.json`'s split, which is what
keeps the frozen bed's gate from moving with it.

**The probe is already run.** §Step 2 says how to re-run it and why you might want to at 1x.
What needs your machine is §Step 4 and §Step 5.

---

## 1. Before you start

| check | how | why it stops the run |
| --- | --- | --- |
| **OS is 26.5** | `sw_vers` → `26.5.2`, build `25F84` | The only reason this session exists. `run-sitting.sh` refuses anything else, first and unconditionally. |
| **Do not update** | Turn off automatic updates before you begin | 27 ships in three days. An update mid-session ends the bed. |
| **Accessibility toggles OFF** | System Settings → Accessibility → Display: *Reduce transparency* off, *Increase contrast* off | For the two standard passes. The harness refuses to file a fixture whose profile key claims a mode the machine is not in, so a wrong toggle is a refusal rather than a silent mislabel — but it costs the pass. |
| **Display scale** | 2x is this machine's native panel. 1x needs the BetterDisplay virtual display, switched by hand between passes. | A profile is captured only on a display whose `backingScaleFactor` matches its key. At the wrong scale the pass captures the other scale's profiles, or nothing. |
| **Screen Recording consent** | `cd apps/reference-apple && open -W --stdout /tmp/probe.log --stderr /tmp/probe.err build/VitreaReference.app --args probe && cat /tmp/probe.log` → must print `ScreenCaptureKit: OK` | TCC is granted per bundle identity, and every rebuild — and every worktree — is a new one. Grant it in System Settings → Privacy & Security → Screen & System Audio Recording, then re-run the probe. Without it every capture fails on the first cell. **Launch the probe through `open`, exactly as `run-sitting.sh` launches every pass**: `./capture.sh probe` execs the same binary from your shell, and macOS then charges the check to the *terminal application* that ran it, so it reports the terminal's grant and not the bundle's (found 2026-09-12: the bundle was granted and the `capture.sh` form still reported TCC; the `open` form printed OK). |
| **Nothing else on the GPU** | close browsers, stop other agents' Playwright suites | `run-sitting.sh` refuses while a capture process is running, and names what it found. |
| **Console session UNLOCKED** | no screen saver, no display sleep, no lock during the sitting | **The harness now refuses a locked screen outright** (`CGSSessionScreenIsLocked`), and the reason is measured: on a locked screen nothing can become active or key, so an active pass would capture the unfocused material under active ids — and an inactive pass is *worse*, because both halves of its attestation are false for the wrong reason and every cell would attest while the window server composites nothing. The idle gate cannot catch it: a locked machine is maximally idle. A `--dry-run` prints `WOULD REFUSE` and continues. |
| **Left alone** | no typing, no other GUI work | Each run refuses unless the machine has been idle 45 s, and idle is sampled per cell. A disturbed run retries rather than filing a disturbed cell. |

Build the harness once, before anything (the Screen Recording grant is against what you build):

```bash
cd apps/reference-apple && ./build.sh
```

---

## 2. Step 1 — the deactivation reading (10 seconds, optional, already recorded)

```bash
cd apps/reference-apple && ./capture.sh deactivate-probe
```

Writes nothing anywhere. It reports what each candidate deactivation mechanism does on this
machine, and its reading is in claims §5.136 and in `Capture.presentInactive`'s doc comment. Run it
if the inactive pass ever refuses and you want to see why; you do not need it to start.

## 3. Step 2 — the labelled vibrancy probe (2 minutes, **already run**)

Already taken and committed: 50 dumps under `packages/calibration/results/2026-09-11-w27e-probe/`,
with the reader's table beside them. Nothing about it needs your machine again. To reproduce it:

```bash
cd apps/reference-apple
IDS=$(python3 -c "import json;print(','.join(s['id'] for s in json.load(open('scenes-w27e-probe.json'))['scenes']))")
for S in light dark; do
  VITREA_SCENES="$PWD/scenes-w27e-probe.json" ./capture.sh dump-layers \
    --scenes "$IDS" --scheme $S --settle 8 \
    --out /tmp/w27e-probe/$S
done
```

`dump-layers` captures no pixels and refuses an `--out` inside the fixture directory, so it cannot
touch the bed. Re-reading the dumps costs nothing and needs no machine state:

```bash
W27E_OUT=/tmp/w27e-reread \
  pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx scripts/vibrancy.ts --corpus probe
```

`W27E_OUT` is not optional: the reader writes create-only (`wx`), so without a scratch directory it
fails with `EEXIST` against the committed table. It reproduces both files byte-for-byte there.

**Worth doing while the display is at 1x for Step 4's 1x pass**, and it needs BOTH window poses.
The probe was taken at 2x through a window that was **not key**; §5.133's corpus is 1x through a
window that **was** key. So two axes differ between the corpora, not one: the scale *and the window
pose this whole wave exists to measure*. A reading in which §5.133's tone-and-span selector holds in
the active pose and the recede collapses to one operator per scheme fits the data just as well as a
scale dependence. The 1x re-run settles it only if it takes both poses — the active one is
`dump-layers`' existing path, and the recede needs the same `.accessory` launch the capture uses:

**The active arm has to be asserted, not assumed.** The committed 2x probe was taken by this same
`dump-layers` with no accessory policy, and all 50 of its dumps record `isKeyWindow: false`:
`capture.sh` execs from a terminal, which does not get the activation a bundle launch does. So an
"active" arm that merely omits the policy can come back non-key, and a run taken to separate the
pose from the scale would produce two non-key corpora and separate nothing. `--require-key` refuses
before it walks a scene, and the active arm goes through `open -W` against the bundle:

```bash
APP="$PWD/build/VitreaReference.app"
# ACTIVE pose, 1x — asserted key, launched the way a bundle is launched
open -W --env VITREA_SCENES="$PWD/scenes-w27e-probe.json" \
  --stdout /tmp/w27e-1x-active.log --stderr /tmp/w27e-1x-active.err "$APP" \
  --args dump-layers --scenes "$IDS" --scheme light --settle 8 --require-key \
  --out /tmp/w27e-probe-1x-active/light
# RECEDE, 1x — same scenes, through the capture's own never-activated path
VITREA_SCENES="$PWD/scenes-w27e-probe.json" \
  ./capture.sh dump-layers --inactive --scenes "$IDS" --scheme light --settle 8 \
  --out /tmp/w27e-probe-1x-recede/light
```

**`--inactive` is the mechanism; the policy variable alone is not** (found 2026-09-12, in the
sitting). The first version of this recipe set only `VITREA_ACTIVATION_POLICY=accessory`, and all 50
dumps it produced at 1x record `isKeyWindow: true`: an `.accessory` application that calls
`activate` still becomes active and its key-capable window still becomes key, and `dump-layers`
did exactly that. The committed 2x probe came out non-key by the accident of its launch context.
`dump-layers --inactive` presents through `Capture.presentInactive` — `.accessory` before the run
loop, a window that cannot become key, ordered front and never activated — and refuses if the
recede is not observed; every dump now records `appIsActive` and `activationPolicy` beside
`isKeyWindow`. The 1x readings of 2026-09-12 are under
`packages/calibration/results/2026-09-12-w27e-probe-1x/`, with the policy-only arm kept as what it
is: the active pose.

Check the two arms disagree before believing either: every dump records its own `isKeyWindow`, so
`grep -h isKeyWindow /tmp/w27e-probe-1x-*/light/*.json | sort -u` must show **both** `true` and
`false`. If it shows only `false`, the active arm did not reach the pose and the run separates
nothing. Write them to NEW directories — never over the committed 2x trees.

## 4. Step 3 — prove the path before spending the machine (~8.5 min for the inactive pass)

Three checks, in this order. The first two need **no machine state at all** — no display, no GUI
session, not even an unlocked screen — so they are the only pre-flight that works from anywhere,
and they pin the regressions that have actually happened here (claims §5.136 §9):

```bash
R=packages/calibration/results/2026-09-11-w27-26.5-run
bash $R/run-sitting.test.sh          # this script's own control flow, harness stubbed
(cd apps/reference-apple && ./capture.sh self-check)   # the pure capture rules, whole truth table
DRY=1 $R/run-sitting.sh inactive 2 1 1                 # the real path, presenting and attesting
```

The third presents and attests every cell of the pass and captures nothing. It exercises every
refusal the real pass has — the fixture root, the backgrounds, the scene resolution, the
presentation and the per-cell pose attestation. Measured at **8 m 19 s** for the inactive pass: the dry path skips the
capture and the settle loop but still pays the 6 s reset interstitial per cell, so it costs roughly
the real pass's dwell and none of its settle. Do it after each toggle change and each scale change
— about half an hour of rehearsals across the whole plan, against a sitting that is hours.

**Read the count, not the verdict.** It must print `cells presented: 76` — 14 for an accessibility
pass, 4 for an active one. A count *under* that is the failure this step exists to catch, and the
script will not catch it for you: it treats any nonzero count as success, so a pass that presented
30 of 76 prints `PASS` and exits 0. On a locked screen it will also print `WOULD REFUSE: … LOCKED`
and carry on, which is correct — the rehearsal captures nothing, and that line is the whole point
of running this early.

## 5. Step 4 — the inactive checking bed, four passes

Each pass is one scale and one accessibility mode; the run count is seven, the probe bar.

```bash
R=packages/calibration/results/2026-09-11-w27-26.5-run

# (a) 2x, standard.  Accessibility toggles OFF, native display.
$R/run-sitting.sh inactive 2 1 7

# (b) 1x, standard.  Switch to the BetterDisplay 1x virtual display first.
$R/run-sitting.sh inactive 1 1 7

# (c) 1x, increased contrast.  System Settings -> Accessibility -> Display -> Increase contrast ON.
#     macOS force-couples Reduce transparency on with it; that coupling is the only reachable
#     increased-contrast state and the harness records it as a profile caveat.
$R/run-sitting.sh inactive 1 1 7

# (d) 1x, reduced transparency.  Increase contrast OFF, Reduce transparency ON.
$R/run-sitting.sh inactive 1 1 7
```

Then the four active cells the new background needs, because a recede is a difference and
`mid-chroma-solid` has no active side yet. Standard toggles, both scales:

```bash
$R/run-sitting.sh active 2 1 7
$R/run-sitting.sh active 1 1 7
```

The script resumes: a run whose `manifest.json` already exists is skipped, so an interrupted pass is
restarted with the same command. A run that FAILS its attestation audit is quarantined under a name
that carries no `manifest.json`, so the same command re-takes it instead of stepping over it — the
resume is safe precisely because a tainted run stops looking like a banked one. Each run goes to its own directory under
`~/vitrea-w27-26.5-run/` (override with `VITREA_SITTING_DIR`), which is what
`cli/materialize.ts` expects — one whole snapshot per run, with nothing decided yet.

**The exact cells** are `bed-inactive.txt` (38 ids) and `bed-active.txt` (4 ids) beside this file,
generated from `results/2026-09-11-w27c-g1b/checking-bed.json`. Per pass, from the profile
declarations and confirmed by the dry run: an inactive standard pass is **38 light + 38 dark = 76**
cells at each scale; each accessibility pass is **14** (the bed's 12-cell checking group plus the
two attestation cells those profiles already declared); each active pass is **4**, light only.

`checking-bed.json` sizes a standard pass at 80, and that figure counts the four active cells
inside it. They are a separate pass here — a different pose, a different command — so they are
counted once, beside it, rather than twice. The bed is the same 42 ids either way; **188 cells per
full round** (76 + 76 + 14 + 14 + 4 + 4), which is what the time below is computed on.

### Expected machine time

At the harness's measured 9.5 s per cell, the four inactive passes plus the two active ones are
**29.8 minutes per run across all passes**, so **3.5 h at the probe bar** before attempt loss, and
**4.5–8.7 h** with the record's own 1.3–2.5× attempt-loss multiplier. §5.134 §5 declared **3.4 h**
and **4.4–8.5 h**; the small difference is the accessibility passes carrying 14 cells rather than
the 12 the specification counted. Plan against the wider number. The freeze bar, which this run is
deliberately **not** taking, would be 8.4 h and 11–21 h.

### What "done" looks like

- Every pass prints `PASS <mode> <scale>x DONE`.
- Every run prints `attested N N` — the two numbers equal. For an inactive run that means every
  cell recorded `presentedActive: false` **and** a `presentation` block whose `observedPose` is
  `inactive` with `isKeyWindow` and `appIsActive` both false. The script stops the pass if any
  cell falls short, because a cell that did not attest its pose is not evidence.
- `~/vitrea-w27-26.5-run/` holds 6 pass directories × 7 run directories, each with its own
  `manifest.json`.

### What to commit, and where

Not the raw runs — they are hundreds of megabytes of PNGs and the repository's practice is that a
sitting's raw snapshots stay on the capture machine. Commit, under
`packages/calibration/results/2026-09-11-w27-26.5-run/`:

- **`sitting.md`** — when each pass ran, the wall-clock per pass, the attested counts per run,
  every retry and what caused it, the display and accessibility state per pass, and the macOS
  build. Model it on `results/2026-09-09-w25-thick-span-composite/g1/sitting.md`.
- **the per-run logs** (`run-*.out` / `run-*.err`) or a distilled digest of them.
- **`provenance.json`** — the run directories, their manifest hashes and their timestamps.

Publishing the bed into the committed fixture bundle is `cli/materialize.ts`, and it is **the next
gate's work, not this session's**: it is where the majority byte-state per cell is decided across
the seven runs, and it needs the G1b read to have declared how the inactive rows enter the bundle.
Leave the raw runs in place and report that they are banked.

---

## 6. What must NOT be done

- **Do not re-run the spent holdout.** The 30-cell holdout of §5.130 is spent; its numbers are on
  the record and re-reading them decides nothing. The checking set is drawn from the 55 declared
  scenes that have no inactive counterpart at all, which is what makes it unspent by construction.
- **Do not treat this as a freeze-bar run.** Seven runs buy the probe bar. No inactive regression
  floor, no adopted bound entry, no `adopted-thresholds.test.ts` change comes out of it. If a
  reading later wants a floor, that is W27c G3 and it needs its own seventeen runs.
- **Do not overwrite a fixture.** A checking-bed cell whose id already exists is a **stop**. Both
  `--inactive` and `--scenes` refuse a fixture root that already holds a `manifest.json`, and the
  script gives each run a fresh one, so this cannot happen by accident — but never point
  `VITREA_FIXTURES` at `apps/reference-apple/fixtures`. A narrowed run republishes each profile it
  captures *wholesale*: it would delete every cell of that profile it did not capture, and the
  merge would strip `recoveredProvenance` from 121 entries and the three run-frequency fields from
  102 more, which `./capture.sh manifest-doctor` will show you at any time.
- **Do not change the scene matrix, a material profile, a golden or the canonical matrix** during
  the session. The bed is declared; the run's job is to execute the declaration, not to improve it.
- **Do not fix up a cell that failed to attest.** Re-run the pass. A cell captured while something
  had activated the app is the one failure the recovered bed cannot rule out about itself, and it
  is exactly what this path exists to stop.
- **Do not take the run on macOS 27.** If the machine has updated, stop and report it: the 27 bed
  is a different decision (a new reference, new profile keys, two axes the key grammar does not
  carry) and it belongs to you, not to this session.

---

## 7. If something refuses

| message | meaning |
| --- | --- |
| `REFUSED: macOS <v> is not 26.5` | The machine updated. Stop; report. |
| `ScreenCaptureKit is unavailable … TCC` | Screen Recording not granted to the process macOS holds responsible. From a pass (launched through `open`) that is the bundle: grant it and re-run the probe through `open` (§1) to confirm. From `./capture.sh <anything that captures>` run by hand it is your terminal application, which is why the runbook never asks for that form. |
| `the machine has been idle Ns, under the 45.0s this run requires` | Expected; the script waits 90 s and retries. Leave the machine alone. |
| `presentInactive: the window is … the application is ACTIVE` | The pose could not be reached before the first cell. Nothing was captured. Run `./capture.sh deactivate-probe`. |
| `scene '<id>': the inactive pose was lost before this cell` | Something activated the app mid-run. Nothing was published. Re-run the pass. |
| `--inactive refuses to publish into …: a manifest.json is already there` | The fixture root is not fresh. Never point it at the committed bundle. |
| `N of the requested scenes declare a state this run's presentation pose cannot reproduce` | An active id in an inactive pass or the reverse. The lists beside this file are the right ones. |
| `Profiles not captured because this display renders at Nx` | The display scale does not match the pass. Switch it and re-run. |
| `the login session's screen is LOCKED` | Unlock the console session and disable display sleep for the sitting. Nothing was captured. |
| `The author tint did not reach the material in this run` | Should not happen on an inactive pass — the recede is exempt from that attestation, because it is measured to remove exactly that response. If it fires on an inactive pass, the exemption did not apply: stop and report. On an **active** pass it means what it says. Rehearse either pose against a bundle with `./capture.sh rehearse-tints --pose <active\|inactive>`. |
| `STOPPING: run N attested X of Y` | A cell failed the four-part audit. The run is **quarantined** to `QUARANTINE-run-N-<timestamp>/`, so re-running the pass re-takes it rather than stepping over it. Keep the quarantined run — what failed to attest is the finding. |
