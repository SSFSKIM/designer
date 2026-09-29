# W42 one-exposure runner (charter clause 11; X26 as carried, X33, X40; Decision Logs 3, 5b)

`runner.py` is the receipt-bound exposure of H: it binds the identified law and both T
candidates, numerical and rendered, to ONE receipt, recaptures the blind rendered H
predictions inside it, and scores all of them in one spent attempt. This directory holds an
instrument proved on a synthetic holdout, not a candidate, an exposure, a browser
measurement or any native reading.

## G0 check

```sh
python3.12 -m unittest discover \
  -s packages/calibration/results/2026-09-29-w42-g0-declaration/bed/exposure -p test_runner.py -v
```

Python 3.12 with Pillow. Every test builds a toy W42-format declaration (a scenes file whose
own split carries calibration, validation, a synthetic H and a probe bridge; a bed.json; a
pins file) in a temporary Git repository and loads it through `bed/wave.py`'s `Wave`; writes
a synthetic archive (generated PNGs and a W39-Reader inventory naming that declaration)
outside the repository; and runs the exposure with injected capture, projection and score
backends and a scratch receipt log. The scorer reads the synthetic held-out pixels through
the guarded Reader with the receipt's token. One test reads the real W42 declaration's
metadata to state the production scope; none opens a payload, launches a browser or the
native harness, or touches `bed/wave-identification-receipt.jsonl`.

- `red.txt`: the 26 first tests against an interface stub (every entry point raising
  `NotImplementedError`): 26 errors.
- `green.txt`: all 27 tests pass (118 s; most of it is Git plumbing in the freeze checks).
- `red-unadmitted-holdout.txt`: the 27th test, added with the change below, fails under
  W41's plan-coverage rule ("authorized web plan" coverage mismatch) and passes under W42's.
- `production-pin.json`: every field null. See "Production" below.

## Reuse, not rewrite: the choice

W41's `runner.py` is imported as a module and **none of its globals is rebound**. Rebinding
`boundary`, `PRODUCTION_LOG` or `INVENTORY_SHA` inside W41's module would work until any W41
function read a constant the rebinding missed, and a test could not see which. So W42 calls
only W41 functions whose behaviour is independent of the wave, unchanged:
`sha, stable, load, git, local, committed, coverage, verify_runtime_artifacts, dimension,
png, persist, capture_web, CaptureRequest, ScoreRequest`. The real browser backend is
W41's `capture_web` itself (a test asserts identity and exercises it with a substituted
process against the W42 scenes file). W39's `Receipt` and `Reader` come through
`bed/wave.py`, which imports them unchanged.

What W42 derives, each because W41 hard-binds it: `sources` (roots), `declared_scope` and
`admitted_scope` (the W42 boundary and a named inventory), `production_pins`, `freeze`,
`verify`, the verdict (`classify`, `tally`, `verdict`), `scratch_path` (the W42 receipt),
`_run`, `run_synthetic` and `run_production`. The derived `_run` keeps W41's lifecycle line
for line: verify before begin; nothing captured or asserted before `begin`; detached
callback snapshots; PNG hash and projection equality against the frozen blind predictions;
runtime-artifact checks after every callback; the full returned scores persisted with
fsync to `<receipt-stem>-scores.json` BEFORE any mutation check or aggregation; the verdict
persisted to `result.json` before the receipt appends `complete`; any failure after begin
appends `failed` and spends H.

## Every behavioural difference from W41

1. **Boundary.** `bed/wave.py`'s `Wave`: the split is in the scenes file (calibration,
   validation, holdout, probe), pinned with bed.json. The production receipt is
   `bed/wave-identification-receipt.jsonl` (created only by G2's exposure); synthetic runs
   refuse it and anything inside the repository, and refuse the production declaration.
2. **Scope.** Numerical: every declared glass cell of calibration, validation and H that the
   bound archive inventory admits. Rendered: its web-plannable subset (the whole of it on the
   W42 bed). Probe bridges (family F) are excluded from both with a stated reason; W41 had no
   probe role. On the real declaration: 414 glass cells, 24 probe exclusions, 390 in scope,
   40 of them H (8 per 2x pass, 2 per 1x pass, all four endpoints), all web-plannable. After
   the parent's s = 32 receded rows: 424 glass cells, 24 probe exclusions, 400 in scope, the
   same 40 H (`synthetic-check.json` `realDeclarationScopeAfterS32Ruling`; `green-s32.txt`).
   After the instrument-stream rulings: 452 glass cells, 24 probe exclusions, 428 in scope, the
   same 40 H (`realDeclarationScopeAfterInstrumentRulings`; `green-rulings.txt`). After
   ruling 3's active guard rows: 465 glass cells, 24 probe exclusions, 441 in scope, the same
   40 H (`realDeclarationScopeAfterRuling3GuardRows`; `green-guard.txt`).
3. **The inventory is named, not fixed.** W41 bound W39's one archive inventory by constant.
   `freeze(..., inventory=...)` binds a committed inventory that must name this declaration
   (`scenesSha256`, `splitSha256` = bed.json); its SHA-256 is the receipt's generation.
   Synthetic mode binds the toy archive's; production binds only the pinned one.
4. **The law and the candidates.** The manifest carries `law` (the identified structure
   through NATIVE T: parameters, numerical predictions over the scope, calibration/validation
   survival) and one `landed-T` candidate plus at most one `native-T` candidate (unique ids
   and roles; a native-T-only manifest refuses, reading Decision Log 5b's "lands instead" as
   presupposing candidate 1). Each candidate carries parameters, its own numerical
   composition, blind rendered predictions (PNG + projection) for the web scope, and
   survival booleans that must all be true on calibration and validation (X33: clause 10
   has passed). All of it is in ONE receipt configuration.
5. **Claimed endpoints (Decision Log 3).** `claimedEndpoints` is frozen: a nonempty subset
   of light/dark x active/receded, each with at least one admitted H cell. Unclaimed
   endpoints are scored and reported `"not claimed (identity)"`; they never affect closure.
6. **The verdict is a result, not an exception.** W41 raised on any failing held-out cell,
   so a scientific failure appended `failed`. Here a completed exposure appends `complete`
   whatever it found, and `result.json` carries the verdict:
   - the law closes iff every measured H cell of every claimed endpoint passes, with at
     least one measured cell per claimed endpoint;
   - candidate 2 (native T): its render against Apple's H pixels;
   - candidate 1 (landed T): its render against its own frozen structure-with-landed-T
     prediction; every measured row must carry `levelMiss` (the gap to Apple, the named
     level miss), which is recorded and never gates;
   - a candidate is `landable` only if the law closes and its own render check passes; one
     candidate's failure never fails the other; `selectedByX40` is candidate 2 if landable,
     else candidate 1 if landable, else none;
   - a law failure leaves nothing landable; H is spent either way.
   Procedural faults (missing or extra cells, sections or candidates, a mutated snapshot or
   capture, a missing `levelMiss`, an UNMEASURED row that is not the censored form) still
   raise and append `failed`.
7. **Censoring (X31, X21).** As W41: a censored row counts toward neither pass nor measured
   coverage, and coverage is reported per endpoint. Different from W41: a censored row whose
   `constraintsPass` is false is a scientific **failure** of that cell (W41 refused it as a
   procedural error).
8. **An H scene the archive did not admit** (a quarantined capture in every profile) is
   excluded at freeze with its reason, and the in-receipt launcher check subtracts it; under
   W41 the launcher's plan would have mismatched the frozen scope inside the receipt and
   spent the exposure procedurally.
9. **What freeze binds.** W41's source roots, plus the Python of W39 G0 and W41 G0 (both
   imported) and of every `results/*-w42-*` tree, so an import added anywhere in W42's
   instrument changes the frozen source inventory. The manifest records `boundarySha256`
   (bed/wave.py), `runnerSha256` (this file) and `inheritedSha256` (W39's wave.py and W41's
   runner.py); `verify` refuses any change. Production also binds bed/pins.json and
   production-pin.json.
10. **The in-receipt scorer request** is W41's `ScoreRequest` unchanged; the law's artifact
    paths are in `request.manifest['law']`. The scorer returns
    `{"law": {"numerical": {cell: row}}, "candidates": {id: {"rendered": {cell: row}}}}`
    over exactly the admitted H cells.

## Production (G1, G0 integration, G2)

`production-pin.json` is committed with every field null, and both `freeze(mode=
'production')` and `run_production` refuse before reading anything else until it is filled:

- `inventoryPath` / `inventorySha256`: **G1** commits the W42 archive's `inventory.json` and
  pins it here (the archive itself is the release asset named by its SHA-256);
- `declarationPath` / `declarationSha256` and `closurePath` / `closureSha256`: the **G0
  integration** that hashes the declaration pins the declaration and the closure rules
  (clauses 6 and 11) the scorer implements.

Then G2, after clause 10's gate, commits the law, the candidates, the blind H renders (made
from the public declaration and the generated backdrop bundle, never from a native fixture),
the runtime-artifact snapshots, the configuration (`fixtures`, `runtimeArtifacts`,
`candidates.<id>.profiles.<key>.{material, receded}`, as W41) and the scorer (`project`,
`score`); calls `freeze(ROOT, default_wave(), candidates, law=..., ..., mode='production')`;
commits the returned manifest; and only then calls `run_production(manifest, output)` once.

## Limits

- The same procedural boundary as W39 and W41, not a sandbox: the committed scorer is
  trusted to implement the declared statistics (max(1 code, bar), the per-channel censoring,
  the seven repeats) and to read Apple's pixels only through the guarded Reader.
- The real browser path and a real W42 archive were not integration-tested in G0; that would
  need a capture. The synthetic proof covers the lifecycle and the checks.
- The pinned inventory is G1's; nothing here infers it.
