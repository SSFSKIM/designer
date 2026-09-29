# W42 sitting tooling (charter clauses 4–5, G1)

The pre-capture instrument for W42's native sitting: it declares how the bed in
`../scenes-w42-body.json` / `../bed.json` is dumped, captured, attested, quarantined and
archived. G0 ran none of it against the native side: no capture, no grant, no GUI launch.
Every file is derived from W39's (G0 `sitting.py`, `record-machine.py`, `pass-spec.py`,
`run-sitting-w39.sh`, the archive tools; G1 `tools/sitting-orchestrate.sh`,
`tools/collect-pass.py`), which stay untouched.

| file | what it is |
| --- | --- |
| `pass-spec.py` | the sitting's membership and order: `plan`, `order`, `spec --pass K --run N [--sentinel]`, `dump-ids --pass K` |
| `sitting.py` | the driver: `plan` (dry), `dump K`, `capture K [first] [last] [--sentinel] [--rehearse-refusal]`, `wait-idle S` |
| `record-machine.py` | the machine and binary read at every run's open and close (W39's, W42 label; by-name census) |
| `run-sitting-w42.sh` | the entry point (`exec python3.12 sitting.py`) |
| `sitting-orchestrate.sh` | the whole sitting in order, one driver call per pass, display switches, stop on any failure |
| `collect-pass.py` | copies a pass's attestations into the G1 evidence directory (never manifests, logs, dumps or PNGs) |
| `w42_archive.py` | `produce`, `verify-tree`, `pack`, `fetch`, `replay`: the archive of record |
| `timing.py` → `timing.json`, `timing.txt` | the sitting's length from real W39 G1 and memo D timings |
| `test_sitting.py`, `test_archive.py` → `test-sitting.txt`, `test-archive.txt` | the proofs, stubs only |
| `dry-plan.txt`, `dry-plan.json`, `dry-plan-stdout.txt` | the dry mode's walk of the whole sitting |

## The sitting, in its one order

1. **Dumps first** (clause 4; charter G1 "First, dump-layers over the declared bed"). One
   `dump-layers` launch per pass, over `bed.json`'s `dumpList` (the `__rest` twin of each of the
   pass's cells: dump-layers refuses non-rest ids in either pose; a receded pass is dumped
   with `--inactive`), settle 8 s as memo D. The 2x endpoints at display mode 68, then the 1x
   endpoints at mode 69: 8 launches, 414 scenes. Each dump directory is checked by
   `../dumps/dumpcheck.py` against memo D's declared configuration (constants, the seventeen span
   laws, the backdrop scale and margin, the pose). **Any departure quarantines the dump and
   stops the sitting before its first capture**; `unpredicted` fields (the active SDF maximum of
   rrect-112, which memo D never dumped) are recorded in `check.json`, not a stop.
2. **Mode 68: the four 2x passes**, light active, light receded, dark active, dark receded,
   seven runs each; the no-glass references of each pass (`ref-<background>__<state>`, one per
   distinct backdrop) in run 1 only. Then the four 2x **sentinel** passes (bed.json's two
   sentinels, three runs each, the long protocol: settle 8 s, order seed 4242).
3. **Mode 69: the four 1x passes and their sentinels**, the same way. The display is restored
   to mode 68 on every exit path.

`pass-spec.py plan` gives the counts: 2,898 glass captures (2x 88 / 86 / 91 / 89 and 1x 15 per
run), 258 references, 48 sentinel captures, 3,204 captures in 80 capture launches, plus 414
dump scenes in 8 launches (`dry-plan.txt`).

## What every run does, and what stops it

Before **every** launch, dumps included: wait, bounded (3 h) and logged in the run's
`driver-idle.log`, for ≥ 75 s of HID idle, unlocked, with no permission prompt on screen (a
prompt stops the wait at once: nobody clicks it). Then read and judge every gate, naming every
failing one in one refusal: macOS 27.0 / 26A428; Reduce Transparency 0, Increase Contrast 0,
`NSGlassTintAmount` 0.5, `ButtonShapesEnabled` 0; display mode (68 for 2x, 69 for 1x) and
identity; the side bundle's binary SHA-256, cdhash and `LC_BUILD_VERSION` against W39 G0's
`bundle-pin.json`; zero foreign processes by name (Chromium, Playwright, `compare.ts`,
`capture-web`, a second `VitreaReference`, Google Chrome, Chrome Helper, headless shells).

A capture run is admitted only if its manifest attests, on every fixture: ScreenCaptureKit,
material rendered, deterministic, the pixel size, the pose (and for receded the observed pose,
not key, not active), **`hidIdleSeconds` ≥ 60** (W39 G1's correction), the window frame
(requested = actual, the canvas size, the backing scale), and each supplied path's
`frameOrigin` = the centred frame **plus the integer `offset`** (the bed places nothing by
`position`); the membership exact; the run label; the capture protocol the launch asked for.
Opening and closing machine reads must agree. A refusal of any kind renames the run
`QUARANTINE-run-N-<ns>` with its `refusal.txt` and every read kept, and stops the pass. There
is never a retry: an existing `run-N` is refused, a later pass that has started blocks an
earlier one, and within a pass run N needs runs 1..N−1 admitted. Continuing is the operator's
explicit act (`START_AT=<pass> FIRST_RUN=<n>` for the orchestrator, or the driver's `first`).

There is no harness `--dry-run` path (W39: it never reaches ScreenCaptureKit, so it proves
nothing about the grant); `DRY` in the environment is refused. The dry mode is
`sitting.py plan`, which writes every derived document and argv and executes nothing. The
TCC-refusal rehearsal, G1's first runbook step while the side bundle is ungranted, is
`capture <pass> --rehearse-refusal` in a root that holds rehearsals only: the real run-1
launch, admitted only as `refused-tcc`.

## Runbook (G1)

All raw roots live outside every checkout and outside `~/Documents`, `~/Desktop` and
`~/Downloads` (W39 G1's Files-and-Folders prompt); the driver refuses otherwise.

```bash
S=packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting
python3.12 $S/sitting.py plan --out /tmp/w42-plan          # executes nothing
# while ungranted, one rehearsal per pose and scale, each at its display mode:
VITREA_SITTING_DIR=~/vitrea-w42/g1/rehearsal bash $S/run-sitting-w42.sh capture 2x-light-active --rehearse-refusal
# after the user's grant switch and the positive pose checks:
VITREA_SITTING_DIR=~/vitrea-w42/g1/run W42_EVIDENCE=<evidence dir> W42_EVIDENCE_REPO=<checkout> \
  bash $S/sitting-orchestrate.sh
```

## The archive of record

```bash
python3.12 $S/w42_archive.py produce ~/vitrea-w42/g1/run --out ~/vitrea-w42/archive
python3.12 $S/w42_archive.py pack ~/vitrea-w42/archive --out-dir ~/vitrea-w42/release   # prints gh commands
ROOT=$(python3.12 $S/w42_archive.py fetch --asset w42-archive-$SHA.tar.zst --sha256 $SHA)
python3.12 $S/w42_archive.py replay "$ROOT" --deny-raw-root ~/vitrea-w42/g1/run
```

`produce` refuses an incomplete sitting (every declared run of every capture pass admitted,
every dump pass admitted) and any existing output. Per captured cell it writes, in the
directory of the cell's role in the scenes file's split (`calibration/`, `validation/`,
`holdout/`, `probe/`), a `states` file (gzip: a JSON header naming every run's pass, run,
protocol, frame SHA-256, attestation, manifest hash and its no-glass reference's frame and
source run, then the distinct **original PNG bytes**, the reference's included) and a
`statistics` file (`analyse` per distinct frame; the default is instrument-free, G1 may pass
the instrument's reader). A reference captured in run 1 serves runs 2–7 and the endpoint's
sentinel runs, and names its source; it never outranks its dependent. Losing states are kept.
The operational record (every run's and quarantine's reads, argv, admission or refusal,
idle log, capture logs, manifests, derived documents, the orchestrator and driver logs) is
filed under `operational/`, every dump JSON and its `check.json` under `dumps/`, each in its
own inventory section outside the role directories, so `../wave.py`'s Reader (W39's) never
serves them to an estimator. The inventory names `scenesSha256` (scenes-w42-body.json) and
`splitSha256` (bed.json), the pair `../wave.py` pins. `pack` writes a deterministic
`w42-archive-<sha256>.tar.zst` under 2 GiB and prints, never runs, the `gh release` commands
(tag `w42-archive`, `--latest=false`). `fetch` verifies the full digest before decompressing
and re-checks a cached tree on every call; `--source` takes the owner's second copy through
the same path. `replay` recomputes every recorded statistic from the archive alone with the
raw root denied; the holdout is refused without the receipt. The repeat bar (clause 5) is
computed from this archive by G1's bar tool with the instrument's reader.

## Length

`timing.txt`: from W39 G1's 40 admitted runs (9.546 s per 2x capture, 9.522 at 1x, 16.0 s
under the long protocol; 11.9 / 11.0 / 18.3 / 17.4 s per run) and memo D's dump runs (8.13 s
per scene at settle 8, 6.2 s per launch), the W42 sitting is **8.62 h of capture + 0.95 h of
dumps ≈ 9.61 h**, against the charter's model of 8.71 h + about 0.96 h. Idle waits beyond the
measured gaps, quarantines, the grant switch and the rehearsal are excluded.
