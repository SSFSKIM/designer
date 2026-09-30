# The bed review of b151aff4: what the fix wave changed

Branch `w42-g0-fix-bed` off `w42-g0-declaration` at `9a695ec0`. One entry per finding the
parent marked FIX (and b8's rulings), each with what changed, its proof and what the parent
folds into the charter, ledger §5.194 and the declaration. The charter, the ledger,
`declaration.json`, `declaration.md` and `declare.py` are untouched here; the SHA-256s and
counts the declaration pins are listed at the end, taken at this branch's head.

## b1 — the active cells no active reader reads are captured receded only

**Changed** (`eb8677e6`, `declare-bed.py`). The two 4-pt patches per scheme
(`c-s8-{hi,lo}-d4-rrect-{md,lg}`), the capsule S 16 patches (`c-s16-{hi,lo}-capsule-button`,
near edge 14 pt in) and D's four outside steps (`d-out{8,16}-{lohi,hilo}-rrect-md`) leave the
2x ACTIVE passes, and `d-out8-lohi-rrect-md` leaves the 1x active passes; all stay in their
receded passes, and their `__rest` scenes become `$dumpOnly` twins. `bed.json`'s U3 text,
charter deviation 3 (now "resolved by b1") and `recordedNotCaptured` say so. On 764217e1's bed
the instrument's `refraction_exclusions` names exactly these 18 cell-passes; on the new bed it
is empty in every pass.

**The instrument's pin** (`e174c15b`, `instrument/bed.py` only): `BED_COMMIT` `eb8677e6`, PINS
scenes `4aa06af9…`, bed `53870f47…`; the module now refuses to load a bed that captures an
active cell the refraction rule excludes (shown firing on 764217e1's bed: 8 cells per 2x active
pass, 1 per 1x active pass). Instrument outputs recorded before this name the pin they ran on
(764217e1 and earlier). The instrument fix wave was told not to edit this file; its reruns read
whichever pin its branch carries.

**New counts.** Glass cells per pass 2x 87 / 92 / 101 / 107, 1x 14 / 16 / 14 / 16 = **447**
(387 at 2x, 60 at 1x; was 465). References 46 / 56 / 56 / 68 and 9 / 10 / 9 / 10 = **264** (was
282). 391 scene entries (was 401), 73 backgrounds and 21 glass components unchanged. Families
per 2x active pass: C 11 light / 20 dark (was 15 / 24), D 7 / 9 (was 11 / 13); 1x active has no
D. Across the eight passes: A 134, B 38, B′ 68, C 75, D 48, E 20, F 24, H 40. Split per 2x pass
63–81 calibration, 12–14 validation, 8 H, 4 F; per 1x pass 8 (active) or 10 (receded)
calibration, 2 validation, 2 H, 2 F. H unchanged: 8 cells, 40 cell-passes. The twin audit is
byte-identical (`a7f2682e…`).

**Reruns.** `declare-bed.py`; the twin audit; the side bundle's `backgrounds` at 1x and 2x and
`self-check` (73 backgrounds, 146 rasters and 82 rows byte-identical to the previous run);
`verify-backgrounds.py` 144 of 146 rasters re-rendered, 14 canonical twins, no problem;
`wave.py plan` 447 of 447 web-plannable; `sitting.py plan` (`dry-plan.txt`): 3,129 glass + 264
references + 48 sentinels = **3,441 captures in 80 launches, 447 dump scenes in 8**;
`timing.py`: **9.25 h of capture + 1.02 h of dumps ≈ 10.31 h** (37,115.5 s; was 10.73 h). Suites
at b1: sitting 21 + 8, runner 27 (`test-*-b1.txt`, `green-b1.txt`); runner scope **423 of 447,
40 H** (`synthetic-check.json` `realDeclarationScopeAfterB1Drops`).

**For the charter** (the parent's): the bed table's per-2x-pass counts become 80 light active /
83 dark active for the charter's own bed (C 9 active, D 7 active; receded unchanged), the 1x
table's edge strip becomes receded only (1x active 14, receded 15, plus the s = 32 row 16), and
the sitting model and the Revision Note's 10.73 h become 10.31 h (9.25 + 1.02).

## B-M1 — the sitting captures and archives only the pinned declaration

**Changed** (`b56e0524`). `sitting.py pin-check` is the orchestrator's first act and the driver
repeats it before every `dump`/`capture`: `wave.Wave()` checks the scenes file and `bed.json`
against `pins.json`; both must equal their committed copies at HEAD; `declaration.json`,
committed, with `declaration.sha256` committed and naming it, must carry both SHA-256s in its
`split` item. A refusal launches nothing and creates no run. Every capture and dump admission
records `scenesSha256` and `splitSha256` (and the whole check record); the order check counts
an admission naming other SHA-256s as not admitted; `produce` refuses such an admission, a
rehearsal's `predeclaration`, and any declared cell left uncaptured. `W42_PREDECLARATION=1`
keeps every check but the declaration's, records its state, and lets the driver launch
rehearsals only (b7 used it, the declaration being unhashed).

**Proof.** In a throwaway Git checkout mirroring the tools (`test_sitting.Mirror`): the
declared bed passes; a scenes file edited by one byte refuses at each layer (pins untouched →
"not its pins"; re-pinned, uncommitted → "differs from its committed copy at HEAD"; re-pinned
and committed → "declaration.json names scenes …"); a stale `bed.json` refuses; an unhashed
declaration refuses; the driver refuses before its root exists; `produce` refuses a declared
cell never captured. `red-green-fixes.txt`: on 9a695ec0's tools the one-byte edit (both ways)
and the stale 764217e1 bed launch and the uncaptured cell archives; on the fixed tools each
refuses. Note: the pin check requires the declaration to be HASHED (`declaration.sha256`),
which `declare.py hash` writes; until the parent hashes, only predeclaration rehearsals run.

## B-M2 — no H pixel statistic outside the receipt

**Changed** (`b56e0524`, `sitting/w42_archive.py`, `wave.py`). `produce` writes each run's
`manifest.json` to `operational/` with every holdout-role fixture reduced to its attestation
fields (`sceneId file fixtureSet orderIndex hidIdleSeconds captureMethod materialRendered width
height deterministic presentedActive presentation suppliedPaths windowFrame capturedAt`) and
the run- and profile-level `caveats` dropped, and its `producer-capture.out`/`.err` with the
diagnostics after every H scene id withheld; the whole files go to a new inventory section,
`holdoutOperational`, under `holdout/operational/`. `wave.py`'s `Reader.read_holdout_operational`
opens them only with an active receipt for the declaration and generation.

**Proof** (`test_archive`, synthetic run whose manifests carry `deltaFromBackground`,
`chromaShift`, `repeatNoise`, `identicalToBackground` and the settle counts on every fixture): no
operational manifest carries any of them for an H fixture while calibration fixtures keep them;
no H line of a public capture log carries `NOISY`; 30 whole files sit under
`holdout/operational/`; the Reader refuses without the receipt, returns the raw manifest byte
for byte inside a scratch W39 receipt, and refuses again after it. `red-green-fixes.txt`: the
pre-fix `produce` leaks all six statistics for H fixtures; the fixed one none.

## b2 — PNG bytes bound at admission

**Changed** (`b56e0524`). Admission requires every fixture PNG the manifest names to exist
inside the run and decode as an RGB(A) PNG at the declared size; `admission.json`
(`w42-run-admission-2`) records each non-H frame's SHA-256 and ONE digest over the H frames
(the admission is published with the G1 evidence; per-run H hashes would publish H's state
frequencies, which W39 G1 kept behind the receipt). `produce` recomputes both and refuses a
difference. **Proof**: missing and wrong-size PNGs quarantine; a changed open frame and a
changed H frame each refuse at `produce`; pre-fix, a run with no PNGs was admitted
(`red-green-fixes.txt`).

## b3 — the orchestrator cannot report success after skipping passes

**Changed** (`b56e0524`, `sitting-orchestrate.sh`). The pass list is computed first and its
exit status and emptiness checked (exit 6), read on fd 3; every child gets `</dev/null` and
`3<&-`; the selection's last pass must be the last reached (exit 4). **Proof**: a driver that
reads stdin gets all 24 passes (pre-fix: 1, then "ALL PASSES DONE"); a failing `pass-spec.py
order` stops with exit 6 (pre-fix: exit 0, "ALL PASSES DONE" with nothing run).

## b4 — every mode change under the trap; the sitting detached

**Changed** (`b56e0524`). The orchestrator re-launches itself under `nohup` in a new session
(`setsid`; pid in `logs/orchestrator.pid`) unless `W42_FOREGROUND=1`; its EXIT trap, reached
from HUP, INT and TERM too, restores mode 68 and verifies it ("restore: display mode 68
(verified)", or "RESTORE FAILED", exit 7). The driver refuses a launch without
`W42_ORCHESTRATED`, which only the orchestrator sets, so no launch, rehearsals included, runs
outside the trap: `REHEARSAL=1 PASSES="…"` runs each named pass as its rehearsal at its mode (a
dump pass as `dump --rehearse`, a bed pass as the TCC-refusal rehearsal). **Proof** (stub
displayplacer): rehearsals switch 69 → 68 → 69 → restore 68; a SIGTERM mid-pass at mode 69 exits
143 with mode 68 restored; a pin refusal with the display left at 69 still restores 68; the
detached orchestrator runs in its own session and completes; a direct driver launch is
refused. The b7 run below was launched this way and ran on while the agent's own background waiters
on it were killed (exit 144).

## b5 — STOP_AFTER=dumps, and the charter's G1 wording

**Changed** (`b56e0524`). `STOP_AFTER=dumps` ends the sitting after the dump step ("DUMPS DONE
… continue with START_AT=2x-light-active"). The runbook (`sitting/README.md`) runs the whole
orchestrator after the user's one switch, the dump step first. **For the charter** (the
parent's amendment): G1's "First, `dump-layers` over the declared bed, while the Mac is idle
and before any grant switch" becomes: the dumps need no grant and run as the sitting's first
phase after the user's one switch (Decision Log 6's single departure); `STOP_AFTER=dumps` runs
them alone.

## b6 — no `rehearse-tints`

**Changed** (`b56e0524`). The receded capture runs no longer call the harness's
`rehearse-tints` (no W42 cell is tinted; it read the main checkout's canonical fixture
manifest and could stop the sitting).

## b7 — the dumps before the sitting

**Run** (`dumps/b7/`, distilled by `dumps/b7/summarize.py` into `b7.txt` and `b7.json`; the
dump JSONs and full machine reads stay in scratch under `~/vitrea-w42/g0-fix-bed-b7/`, hashed in
`scratch-sha256.txt`). The fixed orchestrator at `b56e0524`, detached, `REHEARSAL=1
STOP_AFTER=dumps W42_PREDECLARATION=1` (the declaration unhashed; the pin check read scenes
`4aa06af9…` and bed `53870f47…` at HEAD against `pins.json`), each launch behind the driver's
idle gate (≥ 75 s HID idle, unlocked, no prompt; ≥ 300 s before the mode switch). No grant,
no capture, no prompt appeared, nothing was clicked. Display 68 → 69 at 23:56:22Z →
"restore: display mode 68 (verified)" at 00:04:59Z, read back 68 afterwards.

| launch (mode) | scenes | elapsed | per scene | timeout | margin | departures | 1-min load during |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2x dark receded, the largest pass (68) | 107 | 890.9 s | 8.326 s | 1106 s | 215.1 s | 0 | 167.5 by hand at launch; 31–237 sampled 23:49:45–23:56:10Z (median 84) |
| 1x light active (69) | 14 | 117.2 s | 8.371 s | 223 s | 105.8 s | 0 | 34–63 (median 38) |
| 1x light receded (69) | 16 | 133.8 s | 8.363 s | 242 s | 108.2 s | 0 | 26–59 (median 41) |
| 1x dark active (69) | 14 | 117.0 s | 8.357 s | 223 s | 106.0 s | 0 | 24–32 (median 27) |
| 1x dark receded (69) | 16 | 133.4 s | 8.338 s | 242 s | 108.6 s | 0 | 22–35 (median 28) |

`dumpcheck` found every scene (107 / 14 / 16 / 14 / 16 files and surfaces, none missing or
extra), no departure from memo D's configuration and no unpredicted field in any launch, so
the 1x endpoints, the (1, 1)-offset capsule included, pass it for the first time. The rate is
settle-dominated: 8.33–8.37 s a scene at a load of 25 and at a load of 237 alike. Memo D's
model (8.13 s a scene + 6.2 s a launch, `sitting/timing.txt`) predicts 876 s for the 2x pass
(measured 891, +1.7 %) and 120 s / 136 s at 1x (measured 117 / 134); the timeout
`n (8 + 1.5) + 90` leaves 19 % on the largest pass and ~45 % at 1x. No launch timed out or ran
close, so none was re-run and the timeout is unchanged. The load was sampled outside the
driver (every 15 s; the sampler started 8.4 min into the 2x launch, the coordinator reports
~226 during it); from now on the driver records `loadAverageAtLaunch` / `AtClose` in every
dump's `timing.json`. Foreign census, recorded not enforced (as G0's dumps did): 17 at the 2x
launch's open (Google Chrome and its helpers, a Playwright `cli.js run-cli-server`), 7 at every
other read (Google Chrome and helpers). The 2x dark active pass (101 scenes) and the other
three 2x endpoints were not dumped here; their shapes and poses were dumped in G0's earlier
checks (`s112/`, `s32/`, `rulings/`, `guard/`).

## b8 — near-twins (rulings recorded, no cell changed)

Recorded in `bed/README.md` ("Near-twins, as the parent ruled them"): an exact-backdrop twin
of a canonical holdout is refused and the same geometry at other levels is allowed (a holdout
protects its pixels, not its geometry; the canonical lc16 probe at that geometry was already
read), so the pitch-16 active guard rows on rrect-lg stand; and `b-p5-c64-rrect-lg` beside
`h-p3-c64-rrect-lg` makes that H cell a level-pair transfer test in the active 2x passes, the
s = 112 H cells carrying the span test. **For the declaration**: record both beside the split.

## b9 — one exposure of H across checkouts

**Changed** (`c6adbecb`, `exposure/runner.py`). `claim_exposure` runs before `begin`: `git
fetch --tags --prune origin` (failure refuses), refuse if the receipt log path has history on
any ref (remote-tracking included) or the marker tag exists on origin or locally, then push an
annotated tag at HEAD naming the receipt configuration's SHA-256 (`git push --atomic`). A
remote refuses to create an existing tag, so of two racing checkouts one lands; the loser
refuses and deletes its local tag. `run_production` always claims `w42-h-exposure` on origin;
`run_synthetic` claims only when handed a guard, and refuses the production name. `result.json`
records the marker. **Proof**: `CrossCheckout`, 7 tests against a bare local origin (first
exposure with the marker on origin before H is posed; a second checkout refused before its
`begin`; receipt history on a side branch; on origin only; a lost race; an unreachable remote;
the production name); the runner suite 34 of 34 (`green-fixes.txt`). `b9-proof.txt`: without
the claim a clone exposes the toy H a second time (red); with it a clone of a local origin
refuses before `begin`; live against GitHub, the throwaway tag
`w42-h-exposure-proof-20260929T234313Z` was pushed from this checkout at `b56e0524`, a fresh
GitHub clone refused on it, and it was deleted from GitHub and locally and read back absent.

## b10 — the bed README's numbers

73 backgrounds, 144 of 146 rasters, and every count b1 moved (447 glass cells, 264 references,
391 scene entries, 447 dump scenes, 3,441 captures, 10.31 h, scope 423) are corrected in
`bed/README.md` and `sitting/README.md`.

## What the parent re-pins

Commits on `w42-g0-fix-bed`: `eb8677e6` b1; `e174c15b` the instrument's pin; `b56e0524` B-M1,
B-M2, b2–b6; `c6adbecb` b9; `f4cb08aa` b7 (and the driver's load record); `70485a0d` b8, b10 and
the README index (b10's count corrections landed partly with b1); this file last. The freeze
reads 1,818.

**The split** (`declaration.json` item `split`, and `bed/pins.json`, which already carries them):

- `bed.json` (splitSha256) `53870f4703681644b00ffcfb5ba60a2fb3a9d1ebe25b5c793b99a0b8b3e50762`
- `scenes-w42-body.json` (scenesSha256) `4aa06af90eb527b249fdede3d7d102b06c027069552c07dfc7456b7bd2c43ca0`
- `twin-audit.json` (twinAuditSha256) unchanged, `a7f2682e771f0ecf1725120c698c4cd6588e972b7c3d4dbe37308cc8fa05a06a`
- `perPass`: "2x: 63-81 calibration, 12-14 validation, 8 H, 4 F; 1x: 8-10 calibration, 2
  validation, 2 H, 2 F"; H unchanged (8 cells, 40 cell-passes); b8's two rulings to record.

**The sources the declaration pins**, old → new (bed/ and instrument/bed.py only; nothing
else pinned changed):

| file | was | now |
| --- | --- | --- |
| `bed/README.md` | 5536a52bb379… | `f5d785597248166903f2a8b99c7a234d16a48edb4530073ebfec00065b9ce1b9` |
| `bed/bed.json` | 9047c8da871f… | `53870f4703681644b00ffcfb5ba60a2fb3a9d1ebe25b5c793b99a0b8b3e50762` |
| `bed/declare-bed.py` | 746e126a7c8a… | `d73ca5f8e376870b5a78c056981924cffb87dcb781574b03eccc993173a6619a` |
| `bed/exposure/README.md` | 65d664644692… | `0d50baead9ae277a636f7eae57e763dec0e52413965faa6eef33eec809156c6d` |
| `bed/exposure/runner.py` | 33ce239f4668… | `1d6aa18b17c7ebc23df17c696c592d45c6468a03ebd0e0ac87f4b811407fd1c1` |
| `bed/pins.json` | 2d9b6b9459ea… | `4badfe18bde4520a8a6a891780160bf9dbd71d463400fd4480fab2c18729b2b7` |
| `bed/scenes-w42-body.json` | e2c532d98ed5… | `4aa06af90eb527b249fdede3d7d102b06c027069552c07dfc7456b7bd2c43ca0` |
| `bed/sitting/dry-plan.txt` | 3eb50c11d7af… | `72503ae27d754d97a3cc241db88d1c0fa9991bb3be54a1d10db1056c1928a4f9` |
| `bed/sitting/sitting.py` | 80813fdaf046… | `6edd67eecf2cd856307141a961ce42f207f1727c4bbb55b02101ce60e452cd99` |
| `bed/sitting/timing.txt` | cdf513425b40… | `593806d97a6e6ab20f301b53eb174f37d64e0916f632a430435550b9038b14e6` |
| `bed/sitting/w42_archive.py` | b46780631086… | `b1e582d4ced8101abf85db62d74dce060fbb076ad27be152e7bd7fb4ae4dc3c2` |
| `bed/wave.py` | 24acdb0cd6b1… | `dfb55b4490bf8e67950ed0c7dab8f93c0c20d19e20378b1e43f2efd3754f4166` |
| `bed/web-plan.json` | f4872f179e51… | `16fb739aa549e5e75bbdc0f36116c8754aeabd25aa26ad9248093b0b2ddb3cc7` |
| `instrument/bed.py` | 30460d574b03… | `5b54a05ce4c9b5fedcfb66fbc1ed39fa3e1eeee34c3448d007d13dfaf1c7c184` |

Unchanged: `dumps/dump-reference.json`, `dumps/dumpcheck.py`, the four `dumps/s112/*/check.json`,
`exposure/green-guard.txt`, `runtime-base-sample.json`, `sitting/pass-spec.py`, `twin-audit.json`.

**New files worth pinning** beside them: `sitting/sitting-orchestrate.sh`
`38101f2babc8ef0be509f8c8336786f9b24b8908d6b754e2bb30fc1e3149ec23`; `sitting/red-green-fixes.txt`
`47addb5d63dceda8438b306c66fc3801b3ab892c65ce244d7a73eb10a6c99593`; `sitting/test-sitting-fixes.txt`
`83e55a19fa6ccabf1bdd02afc4026fbba4e07a4ba7aea40cad026681b00eecc4`; `sitting/test-archive-fixes.txt`
`23034406974a7ab20352b438800727d521ce95583715a1ce9387a8ae200329a2`; `exposure/green-fixes.txt`
`e1d0edbed812e51f767bdeb09312ec5b17d68d5de9c914b950775feddb921181`; `exposure/b9-proof.txt`
`c3cb84e6084a1b5b530a47cdb17b11d40309093b7efdc2e1156483c49369de1b`; `dumps/b7/b7.txt`
`a03ba71c48388575af5f8270df0597e96878ed5ca148d07ed7fa30a52fb8b58c`.

**What `declare.py` hard-codes and must follow** (it is the parent's): the dry-plan totals
`{"dumpLaunches": 8, "dumpScenes": 447, "captureLaunches": 80, "glass": 3129, "references":
264, "sentinels": 48, "captures": 3441}`; the timing line `TOTAL      37115.5 s = 10.31 h`; the
runner scope `(423, 40)`. `declare.py check` at this head reports 23 mismatches: the 14 changed
pins above, the three split pins, the `bed` item's per-pass, total and reference counts, the web
plan's total, and the sitting's totals and 10.73 h. The runner-scope line still passes only
because the declared `glassCells` is still 465; once it reads 447 the hard-coded `441` must read
`423`.

**Declaration items whose text moves**: `bed` (`glassCells` 447, `perPass` 87 / 92 / 101 / 107 /
14 / 16 / 14 / 16, `references` 264, `growth` "… − 18 active cell-passes no active reader read
(b1, eb8677e6)", deviation 3 resolved by b1); `refractionOrder.exclusions` (on the bed they are
now empty: the cells are receded only); `sitting` (447 dump scenes, 3,129 + 264 + 48 = 3,441, 10.31 h =
9.25 + 1.02, the pin check, STOP_AFTER=dumps, the detached orchestrator, rehearsals through
it); `exposureRunner.scope` ("423 of 447, 40 of them H") and the b9 claim; `webPlan.result`
(447). **The charter and §5.194**: b1's counts and length, b5's G1 wording, b4's runbook, b9's
cross-checkout claim, b7's reading.
