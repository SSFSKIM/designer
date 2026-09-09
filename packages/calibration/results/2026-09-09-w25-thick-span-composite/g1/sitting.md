# W25 G1 — the sitting: what the harness captures, in what order, and what is checked after

The declaration half of G1 is done and committed; this file is the other half's instruction sheet.
It is written for the parent at the capture machine with the user present, and everything in it is
either a command to run or a number to check a result against. Nothing here has been run: no
fixture, no matrix and no web capture was written by the declaring worker (contract X2).

The set it captures is declared in `apps/reference-apple/scenes.json` as the `probe` fixture set
(W25 Decision Log 3 (e); claims §5.113). 52 scenes, on the four standard profiles and on neither
accessibility profile.

---

## 0. Before the sitting: one rebuild, and the grant that follows it

**A rebuild is required, and it is the only one.** The `probe` role is a fifth entry in the scene
matrix's `split`, and the harness refuses a matrix it cannot give every scene a role in — by
design, because a scene silently treated as `calibration` is how a holdout leaks into tuning. The
binary on disk was compiled before the role existed. Verified, not assumed: the committed harness
loaded against the new matrix answers

```
error: cannot load .../scenes.json: scenes.json is inconsistent:
  - scene 'checkerboard-4__rrect-sm__rest' is in no split set
  - … 51 more
```

The three-line Swift change that teaches it the role is committed (`SplitSpec.probe` and its two
call sites in `SceneSpec.swift`, `SplitDeclaration.probe` in `Manifest.swift`, the manifest's split
block in `main.swift`). It has been compiled and exercised out of tree — a binary built from these
sources at `/tmp` loads the new matrix, validates it, and draws all fourteen backgrounds
byte-stably — but `build.sh` itself has **not** been run, because a rebuild re-signs the bundle ad
hoc and the Screen Recording grant is keyed to that signature.

So the sitting begins with, in the main checkout:

```bash
cd /Users/new/developer/github/designer/apps/reference-apple && ./build.sh
```

and then, with the user: System Settings → Privacy & Security → Screen & System Audio Recording →
remove `VitreaReference.app` and add it again (a recorded denial suppresses the prompt, so
toggling an existing entry off and on is not always enough). One `./capture.sh probe` answering
`screencapturekit` before the first real run is what confirms the grant came back.

**No new background generator is needed, and nothing else in the harness changes.** Every backdrop
the set adds is an existing kind at another parameter — a checkerboard at cell 4, 8, 32 or 64, a
low-contrast checkerboard at 16, text rows at 7 and 28 — and the fourteen rasters the rebuilt
binary draws include all seven new ones. Each of the thirteen that the W21 grid also carries is
**byte-identical** to that grid's committed raster, so the grid's readings and the sitting's are
over the same backdrops down to the byte.

---

## 1. Pre-flight, in this order

Each of these has cost a session before, and each answers in a second.

```bash
# (a) The GPU is shared, and one capture process at a time is contract X4.
pgrep -f 'compare.ts|sweep.ts|cost.mjs|capture.mjs|capture-web|VitreaReference|playwright'   # expect: no output
lsof -i :5189                                                                                # expect: no output

# (b) The console session must be UNLOCKED, which is not the same as being on console.
ioreg -n Root -d1 -a | plutil -extract IOConsoleUsers xml1 -o - - | grep -A1 CGSSessionScreenIsLocked
#   … <false/>   → good.  <true/> → refuse: loginwindow is frontmost, no window can be made key,
#   and every cell records Liquid Glass's flat inactive pose and fails presentedActive.
#   Screen Sharing does NOT unlock the console session (claims §5.17; W21 G0's blocker, W25
#   Decision Log 2 (b)). Ask the user to unlock the physical console at this moment.

# (c) Accessibility must be in the standard state, or the two a11y profiles are skipped — which
#     is fine and recorded, but the run should say so on purpose rather than by accident.
#     Reduce Transparency and Increase Contrast both OFF.

# (d) For the 2x half only: the display must actually report backingScaleFactor 2 (the virtual
#     HiDPI arrangement the 2x bed was captured on). The harness records the real scale and
#     refuses to file 2x pixels under a 1x key, so a wrong display fails loudly rather than
#     quietly. `capture.sh`'s and README's paragraphs claiming scenes.json has no 2x profiles
#     predate W1 and are stale; the profiles are there and their fixtures are committed.
```

---

## 2. What is captured, and how much of it

| profile | scenes | of them probe | captured at |
| --- | --- | --- | --- |
| `apple-macos-26.5-1x-light-standard` | 92 | 52 | the 1x pass |
| `apple-macos-26.5-1x-dark-standard` | 66 | 52 | the 1x pass |
| `apple-macos-26.5-2x-light-standard` | 92 | 52 | the 2x pass |
| `apple-macos-26.5-2x-dark-standard` | 66 | 52 | the 2x pass |
| `apple-macos-26.5-1x-light-reduced-transparency` | 9 | 0 | not this sitting |
| `apple-macos-26.5-1x-light-increased-contrast` | 10 | 0 | not this sitting |

Both schemes are captured in **one run per scale** — the harness pins `\.colorScheme` per profile —
so the sitting is two passes, not four.

- **158 fixtures per run** (92 + 66), each run about 25 minutes at the grids' 9.5 s per cell.
- **316 fixtures per attested run-pair**, of which **208 are the probe set** (52 × 4 profiles).
- **208 fixtures are published.** The other 108 are captured into the run snapshot and never
  published: they are the frozen bed's own cells, and re-publishing them would replace the bed the
  whole ledger is measured against with this sitting's bytes. `materialize --set probe` is what
  makes that structural rather than careful — see §4.

---

## 3. The runs

The protocol is W9's, which W21 re-ran and W25 G0 read: a 6 s bare neutral reset before each cell,
the one fixed capture order (no `--order-seed`), the run refused unless the machine has been idle
45 s, and the bed materialised from the **majority byte-state per cell across the attested runs**.
That protocol is not decoration — it is the only reason the dark grid can say that
`dark-solid__rrect-md` and `-lg` are single-state in all seven runs while `rrect-sm` is bistable at
6:1, which is the finding W25 was re-scoped on.

`capture.sh` supports repeated runs by writing a *whole bundle* per invocation: point
`VITREA_FIXTURES` at a fresh directory and each run is a complete, independent snapshot — profile
directories plus that run's own `manifest.json` — with nothing decided yet. `cli/materialize.ts`
then decides per cell across those snapshots.

**Budget: seven attested runs per scale.** W21 banked seven attested of eighteen attempted; the
tracker's "the reference harness loses cells to window activation with the machine idle" is why.
Seven runs buy 72 % confidence that a state held by one draw in six was seen at least once; five
buy 60 %, and five is the floor worth publishing at if the session has to be cut short. The
provenance block records whichever it was.

`results/2026-09-06-w21-dark-scheme/g0/run-probe.sh` is the runner to copy, with three changes:
`VITREA_SCENES` dropped (the set is canonical now, so no override), `--run-label w25-1x-N`, and
`VITREA_SCALE=2` on the second pass. Its shape matters and should be kept:

```bash
APP=/Users/new/developer/github/designer/apps/reference-apple/build/VitreaReference.app
HARNESS=/Users/new/developer/github/designer/apps/reference-apple/build/harness
T=/Users/new/.claude/scratch/w25-sitting          # any scratch root outside the repo

# --- the 1x pass, runs 1..N
for N in $(seq 1 7); do
  D="$T/1x/run-$N"; mkdir -p "$D"
  VITREA_FIXTURES="$D" "$HARNESS" backgrounds
  open -W --env VITREA_FIXTURES="$D" --stdout "$D.out" --stderr "$D.err" "$APP" \
    --args capture --run-label "w25-1x-$N" --reset-interstitial 6 --min-idle-seconds 45
done

# --- the 2x pass, on the 2x display
for N in $(seq 1 7); do
  D="$T/2x/run-$N"; mkdir -p "$D"
  VITREA_SCALE=2 VITREA_FIXTURES="$D" "$HARNESS" backgrounds
  open -W --env VITREA_SCALE=2 --env VITREA_FIXTURES="$D" --stdout "$D.out" --stderr "$D.err" \
    "$APP" --args capture --run-label "w25-2x-$N" --reset-interstitial 6 --min-idle-seconds 45
done
```

Three things in that snippet are load-bearing:

- **`open --env`, not the environment of the calling shell.** `launchctl setenv` never reaches the
  GUI session `open` launches into, and a harness that sees no `VITREA_FIXTURES` writes the
  canonical bed. Run `backgrounds` through the symlinked binary directly (it needs no bundle
  identity), and `capture` through the `.app` (the Screen Recording grant is on that identity).
- **`backgrounds` before `capture`, per run and per scale.** `capture` composites the backgrounds
  in memory and then verifies each recorded PNG against what it composited, refusing on a stale
  one. The 2x rasters are separate files keyed `name@2x`.
- **The first run is the budget's own pre-flight.** If it attests well under 158 of 158 cells, the
  session is in a state the protocol cannot see and the remaining runs buy nothing; report the
  session state instead of spending them. W21's script stops at that check and it should be kept.

**Audit attestation before materialising.** `materialize` does not read `presentedActive` — it
publishes bytes — so a run in which the window was never key would publish a photograph of the flat
inactive pose. Per run:

```bash
python3 - "$D/manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
for p in m["profiles"]:
    f = p["fixtures"]
    ok = [x for x in f if x["presentedActive"] and x["deterministic"] and x["materialRendered"]]
    print(p["profileKey"], len(ok), "/", len(f))
PY
```

A run with a failing cell is excluded by name and the exclusion is written into the sitting's
`provenance.json`, never silently dropped.

---

## 4. Publishing: the probe cells only

```bash
cd /Users/new/developer/github/designer/packages/calibration

ARGS=(); for D in "$T"/1x/run-*; do ARGS+=(--run "$(basename "$D")=$D"); done
npx tsx cli/materialize.ts "${ARGS[@]}" --set probe --frequency-settle            # dry run
npx tsx cli/materialize.ts "${ARGS[@]}" --set probe --frequency-settle --apply    # writes

# then the same for "$T"/2x/run-*
```

`--set probe` is W25's addition and the reason this can be done at all: publication is otherwise by
whole profile directory, and a run that adds cells to a bed republishes every old one beside them —
the sitting's bytes over the frozen bed's, silently, with the gate then reading a bed nobody meant
to re-capture. With the filter, the 108 frozen-bed cells in each run are skipped before their bytes
are read. `--frequency-settle` publishes a bistable cell at its majority state with the observed
shares recorded; a tie is still refused, and a refusal is the finding rather than an error to
route around.

**Two things `materialize` does not do, and the sitting must.**

1. **The seven new background rasters.** Copy them into `apps/reference-apple/fixtures/backgrounds/`
   at both scales — `checkerboard-4`, `-8`, `-32`, `-64`, `checkerboard-lc16`, `hc-text-7`,
   `hc-text-28`, so fourteen files — and add their `name@1x` / `name@2x` entries to
   `fixtures/manifest.json`'s `backgrounds` map from an attested run's manifest. Without them
   `compare` refuses every probe cell with "the manifest has no background 'checkerboard-32' at 1x",
   which is the right refusal and not one to work around.
2. **Cross-check the rasters that already existed.** Each background the bed already carries should
   be byte-identical between the sitting's runs and `fixtures/backgrounds/`; a difference is a
   generator drift and stops the sitting, because every fidelity number over that backdrop on both
   beds would then be measured against two different backdrops.

Then commit — the fixtures and the manifest are committed evidence, and G1 is the child that writes
them (X2).

---

## 5. What the parent checks after

**(a) The two withdrawn cells are no longer the light grid's files.** This is the sitting's own
acceptance. `dark-solid__rrect-sm__rest` and `light-solid__rrect-sm__rest` in the W21 dark grid have
a majority byte-state identical to the W9 **light** grid's capture of the same scene — for
`light-solid` unambiguously so (a body of 0.96659 over a 0.8918 backdrop is a light-scheme frame),
and both were withdrawn as dark readings on that evidence (claims §5.113; Decision Log 3 (d)).

```bash
cd /Users/new/developer/github/designer
for S in dark-solid__rrect-sm__rest light-solid__rrect-sm__rest; do
  shasum -a 256 \
    "packages/calibration/results/2026-09-02-w9-probe/apple-macos-26.5-1x-light-standard/$S.png" \
    "apps/reference-apple/fixtures/apple-macos-26.5-1x-dark-standard/$S.png" \
    "apps/reference-apple/fixtures/apple-macos-26.5-1x-light-standard/$S.png"
done
```

The dark capture must differ from the W9 light grid's file. If it does not — if the dark profile
once again returns the light grid's bytes on these two cells and only these two — that is not a
capture failure to retry silently: it is the flip reproducing under a controlled protocol, which is
a stronger finding than the withdrawal was, and it belongs in the claims section with the run
frequencies beside it. Read the light-scheme capture of the same ids in the same sitting as the
control: it is what the bytes *should* look like if the scheme did not take.

**(b) The bistable share, per cell.** The grids' own value was that they recorded it. Same
instrument:

```bash
cd /Users/new/developer/github/designer/packages/calibration
npx tsx cli/stability.ts --label w25-1x --runs "$(ls -d "$T"/1x/run-* | paste -sd, -)"
npx tsx cli/stability.ts --label w25-2x --runs "$(ls -d "$T"/2x/run-* | paste -sd, -)"
```

It classifies every cell as deterministic, bistable, multi-state, noisy or unattested over the
runs that attested it, by the same rule `materialize` publishes with. What to read out of it:

- the **share per bistable cell**, which is what the published `stateFrequencies` in the manifest
  then carries;
- whether the seven `dark-solid` spans (32, 48, 64, 80, 96, 128, 160 — `rrect-sm`, `rrect-48`,
  `rrect-64`, `rrect-80`, `rrect-md`, `rrect-ml`, `rrect-lg`) are single-state, because the
  collapse's key is read off them and a bistable cell in that sweep is a state flip rather than a
  size law (Decision Log 3 (d), clause 5);
- whether `dark-solid__rrect-md__rest` and `dark-solid__rrect-md-clear20__rest` differ. Same span,
  clearance 52 against 20. If the second collapses and the first does not, the collapse keys on
  edge proximity and not on size, and every fixture on disk was consistent with both.

**(c) The sitting's provenance.** Write `provenance.json` beside the published cells in W21's shape:
the runs materialised from, the runs excluded and why, the rule, the per-run attestation audit, the
idle seconds at each run's start and end, and the toolchain block. "Deterministic" is a claim about
how hard anyone looked.

---

## 6. What this set does not cover, and why — for the record

Two residuals, both created by the rule that the gate must not move, both recorded rather than
worked around.

1. **Five grid cells cannot be re-captured under the dark scheme.**
   `checkerboard__rrect-sm__rest`, `checkerboard__rrect-ml__rest`, `checkerboard__rrect-lg__rest`,
   `hc-text__rrect-md__rest` and `photo__rrect-sm__rest` are grid cells whose ids are **also**
   canonical bed cells, in `calibration`, `validation` or `holdout`. The dark profiles do not list
   them, and adding them would add gated dark rows — moving the gate's counts, its predicate
   exclusions and possibly its floors, which Decision Log 3 (e) forbids this set from doing. The
   W21 grid's own fixtures remain the dark reading for them. Closing this needs either a gate
   re-derivation (a landing child's work, with the user) or the acceptance that the pitch-16 column
   in dark is read from the grid rather than from the bed.
2. **`impulse__rrect-md__rest` has no dark row for the same reason** — it is a canonical
   `validation` cell. Reader A's two-component decomposition at span 96 is therefore a light-scheme
   reading at both scales, and the dark scheme's kernel is read at spans 32, 128 and 160 through
   `impulse__rrect-sm`, `-ml` and `-lg`, which the set does add.

Both belong in `specs/tech-debt-tracker.md` if they are still open when the wave lands.
