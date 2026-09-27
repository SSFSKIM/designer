# W41 renderer-bound single exposure

Clauses 2/11, X26, X31 v2.2, claims §5.191. `runner.py` extends the inherited W39
`wave.py` boundary without modifying it. This directory contains an instrument,
not a candidate, exposure, browser measurement or native reading.

## G0 check

```sh
python3.12 -m unittest discover \
  -s packages/calibration/results/2026-09-27-w41-g0-declaration/exposure \
  -p test_runner.py -v
```

Python 3.12 and Pillow suffice. The tests create temporary Git repositories,
copy **metadata only** from the W39 Wave, freeze committed synthetic predictions,
write 2×2 synthetic RGB images through an injected backend, and measure both
numerical predictions and those new images against independent `[80,90,100]`
observations. Their receipts are temporary scratch files, not the W39 log.
The synthetic receipt does not authorize the W39 inventory generation.

Tests were run RED with `freeze` unimplemented, then GREEN. Additional RED/GREEN
checks caught a scratch token inadvertently authorizing the native generation
and a captured image changed during scoring. See `synthetic-check.json` for the
recorded dry-run numbers. One separate test exercises the real subprocess
backend's command construction and output/provenance parsing using a substituted
process; **it does not launch Chromium**. No native payload, archive Reader,
native bundle, matrix CLI, browser or actual web capture was used in G0.

## Freeze contract for G1

The entry points are Python APIs, intentionally not an `expose` CLI that can be
run accidentally. Production cannot take a log path or an injected backend.
`run_synthetic` cannot accept a production manifest and must use paths outside
the evidence repository; it does not open or inspect the production receipt.

1. Commit the renderer, its numerical candidates, its configuration, its scorer
   and every prediction payload. A candidate is an implemented surviving
   **composite** (body/stroke operators and their held surroundings), not a
   numerical-only family that would evade the rendered referee. Different
   composites have different candidate IDs and document pairs. Spatial findings
   and failed families are frozen as supplementary artifacts, not carried as
   landable survivors (Decision Log 6).
2. Call `freeze(ROOT, wave, candidates, config=..., scorer=...,
   declaration=..., closure=..., instruments=[...])`. Use `wave =
   runner.boundary.default_wave()`. Production requires the unchanged W41 G0
   `bounds-declaration.txt` and `closure.json`. Pass repository-relative paths.
3. Write the returned object as, for example, `frozen.json`, and **commit it**.
   A later manifest-only commit may change HEAD; frozen source bytes must still
   match both HEAD and the recorded `revision`. Uncommitted inputs are refused.
4. Only when G1 authorizes its single exposure, call
   `run_production(ROOT / '.../frozen.json', Path('/tmp/w41-g1-exposure'))`.
   The output directory must not exist. This is the only production execution
   entry point. It uses W39 G0's `wave-identification-receipt.jsonl` without an
   alternate path, retry or replacement generation.

`manifest.schema.json` describes the freeze envelope and the payload shapes.
Paths are explicit, not discovered by candidate naming conventions. A typical
`candidates` entry is

```json
{
  "id": "composite-e3-m1",
  "parameters": "path/to/parameters.json",
  "predictions": "path/to/numerical-predictions.json",
  "rendered": "path/to/rendered-predictions.json",
  "survival": "path/to/survival.json"
}
```

The files have these contracts:

- `parameters.json`: nonempty JSON holding **every frozen numerical coefficient**.
- `numerical-predictions.json`: `{"cells":{"profile/scene":<prediction>,...}}`.
  Supply every glass cell across calibration, validation and holdout, including
  the native-only cells. The numerical instrument owns each prediction's inner
  shape; it must not be empty or contain NaN/Infinity. A prediction is a forward
  output, not a path or digest substituting for its payload.
- `rendered-predictions.json`: `{"cells":{"profile/scene":{"png":"path.png",
  "projection":"path.json"},...}}`. Supply every **web-plannable** glass cell
  across all three roles. Each PNG is decoded and dimension-checked. Each
  projection is finite JSON from the same `project` routine used during exposure.
  Frozen held-out **web** predictions contain no native measurement; native
  holdout remains unopened. No missing PNG can be replaced by a numerical output.
- `survival.json`: `{"numerical":{"profile/scene":true,...},
  "rendered":{"profile/scene":true,...}}`. These are the scorer's admission
  summaries for every calibration/validation cell in the respective scope;
  A `true` means every admitted constraint is met: measured channels satisfy
  max(1,bar), rail channels satisfy their hard one-sided bounds, and deficient
  bins are excluded and counted under X31 v2.2. `false`, missing, extra or holdout
  entries refuse freeze. Include the detailed
  survival/veto reports in `instruments` too: the booleans are admission, **not a
  substitute for the charter's per-channel/bin, seven-repeat proof**.
- The configuration is
  `{"fixtures":"path/to/generated-web-backdrops","candidates":{
  "composite-e3-m1":{"profiles":{"profile-key":{"material":"active.json",
  "receded":"receded.json"}}}}}`. Every candidate needs all rendered profiles.
  Both material document bytes are frozen. These are scratch candidate documents,
  not resealed shipped profiles. The fixture directory is a **generated web
  backdrop bundle**, not the native archive: its `manifest.json` contains only
  optional `schema` and `backgrounds` (`"background-id@1x":"relative.png"` and
  `@2x`). Every required background PNG is frozen, decoded and dimension-checked.
  G1 supplies these non-captured sRGB rasters; this runner never runs the native
  harness to create them or mounts a native capture tree.
- `scorer.py`: the committed scoring module described below. `instruments` lists
  any other imported code, numerical inputs, resolved-material sidecars, spatial
  findings, veto reports and configuration that determine predictions or scores.

`files` in the manifest maps **every input path to its full SHA-256**. In
addition, the runner automatically freezes the source-aliased runtime packages,
calibration web/scripts/src, package manifests, workspace/lock files, and all
Python sources in the W39 G0/G2 and W41 G0 instrument trees. Added or deleted
source files are changes too. `revision` names the source commit;
`boundarySha256` and `runnerSha256` name the executing Python boundary;
`scenes`, `split`, `generation`, `sourceFiles`, `numericalCells` and
`renderedCells` pin the membership and source inventories. The sole production
`generation` is W39's inventory SHA `58329732…35f61`.

## Scorer interface and authority

Production loads the committed module **inside the active Receipt**, never at
preflight. It must export

```python
def project(cell: str, png: pathlib.Path) -> JSON: ...
def score(request: runner.ScoreRequest) -> JSON: ...
```

`project` is a deterministic, web-only projection of an image using the same
geometry/bin/deep-body reader used for native scoring; it must not read native
payloads. It may use pinned scene metadata and other declared instrument inputs.

`ScoreRequest` provides `wave`, `authorization`, `root`, `manifest`,
`candidates` (ID → artifact specification), `numerical_cells`, `rendered_cells`,
and `captures` (candidate ID → cell → **fresh capture path**). The scorer must
construct archive Readers using this token, verify their inventory generation,
and use the guarded archive accessors for every native pixel/reference/repeat.
It must score the fresh web images, not just the frozen numerical projections.
It must retain per-channel censor constraints, required bins, populations and all
seven repeats, and return detailed evidence alongside these mandatory summaries:

```json
{
  "composite-e3-m1": {
    "numerical": {"profile/scene": {"status":"measured", "passes":true}},
    "rendered": {"profile/scene": {"status":"measured", "passes":true}}
  }
}
```

The top-level candidate, kind and cell sets must be exact. A required cell
containing censoring has status `UNMEASURED` for held-out coverage even if its
individual rail constraints are `censored-bound-satisfied`; detailed channel/bin
statuses remain in the report. Under X31 v2.2, return the excluded cell as
`{"status":"UNMEASURED","reason":"censored","passes":null,
"constraintsPass":true}`. The last field attests that every uncensored
comparison and every one-sided rail constraint still passes; censoring cannot
hide a binding failure. The runner counts this cell toward neither passes nor
measured coverage, and reports `measured`, `censored`, `total` and `fraction`
for each candidate/kind. Every measured cell must pass. Other UNMEASURED reasons,
missing cells, or `constraintsPass:false` refuse completion. Deficient individual
bins are excluded and counted by the scorer, not silently treated as zero error.

The numerical scope includes grey-255's bottom pair; the rendered scope excludes
it by the inherited placement rule, not a handwritten allowlist. Use the shared
`instrument/rendered.py::score_capture(png, payloads7, baseline=None)` for the
rendered scoring: it takes seven **already guarded** native payload dicts and
opens no native files itself. The G1 scorer owns their admission and turns its
per-channel/bin results into the summaries above. It must preserve the full
scorer output, including population-deficient bins, alongside those summaries.

## What happens inside the receipt

`capture_web` launches the existing `scripts/capture-web.ts` directly through
pnpm/tsx, once per candidate/profile. It does not invoke `compare`, a matrix
writer, the native harness or a native Reader. It clears inherited `VITREA_*`
overrides, selects the frozen scenes/backdrops/document pair, requests WebGPU
in full Chromium, and disables software-adapter fallback. It verifies the
returned scene, dimensions, actual renderer, material hashes, determinism and
absence of fallback/problems. The driver's two page loads measure determinism;
there is no retry of a failed attempt.

Every returned cell must be present under the fresh output directory, have the
**identical PNG bytes** to its frozen web prediction and reproduce its projection
exactly. Then the native scorer runs. Frozen inputs are reverified after capture
and after scoring, and the fresh PNGs are rehashed after scoring. Results are
written and fsynced to `result.json` before W39 can append `complete`.

A failure after `begin` appends `failed` and consumes the entire exposure. An
interruption follows inherited W39 lock/spent semantics. Preflight mutation,
missing candidate payload or incomplete frozen coverage refuses before `begin`.
Once spent, a changed candidate cannot obtain another attempt. No path here
changes the inherited W39 source, declaration, split or protected evidence.

## Limits and integration stops

- This is the same **procedural**, not hostile-code security boundary as W39.
  Committed scorer code is trusted to implement the declared statistics, use
  guarded Readers and list transitive inputs. The runner checks its outputs and
  authority lifecycle; it is not a Python sandbox or a second numerical solver.
- A source/lock freeze does not attest installed dependency bytes or the GPU/OS.
  G1 must install from the frozen lock and use its attested capture environment.
  Exact output/projection comparison prevents a changed rendered prediction
  from inheriting closure; nondeterministic rendering spends the attempt.
- Production requires G1's renderer/document pair, generated backdrop bundle,
  full numerical/rendered predictions, admission proofs and scorer. None exists
  by inference here. The native callback and real Chromium execution were **not
  integration-tested in G0**; doing so would violate G0's no-capture/no-exposure
  constraints. The synthetic proof verifies the lifecycle and checks only.
- Because all callbacks and code must be frozen, a later scorer or operator edit
  needs a new pre-exposure freeze. Once exposed, it cannot reopen this archive.
