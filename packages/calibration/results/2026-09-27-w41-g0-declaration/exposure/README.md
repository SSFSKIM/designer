# W41 renderer-bound single exposure

Clauses 2/11 (charter v2.3), X26, X31 v2.2, claims §5.191. `runner.py` extends the inherited W39
`wave.py` boundary without modifying it. This directory contains an instrument,
not a candidate, exposure, browser measurement or native reading.

## G0 check

```sh
python3.12 -m unittest discover \
  -s packages/calibration/results/2026-09-27-w41-g0-declaration/exposure \
  -p test_runner.py -v
```

Python 3.12 and Pillow suffice. The tests create temporary Git repositories,
copy **metadata only** from the W39 Wave and fixed committed archive inventory,
freeze committed synthetic predictions, write 2×2 synthetic RGB images through an injected backend, and measure both
numerical predictions and those new images against independent `[80,90,100]`
observations. Their receipts are temporary scratch files, not the W39 log.
The synthetic receipt does not authorize the W39 inventory generation.

Tests were run RED with `freeze` unimplemented, then GREEN. Additional RED/GREEN
checks caught a scratch token inadvertently authorizing the native generation
and a captured image changed during scoring. The bounded fix wave adds eight
regressions: a failed score is fsynced before aggregation, a freeze failure retains
that score, a scorer exception records failure without invented scores, callback
manifest/candidate/capture-map mutation cannot rewrite the trusted comparisons,
and a child killed with SIGKILL between score persistence and verdict leaves its
scores beside the spent scratch receipt. `fix-wave-red.txt` records 24 tests with
four failures and four missing-evidence errors before the fixes;
`fix-wave-green.txt` records all 24 passing. The second fix wave adds 17 tests:
production freeze uses the real inventory metadata with synthetic predictions,
refuses omitted/admission-tampered cells, and checks compiled policy bytes and
module inventory before begin and after callbacks. `admission-runtime-red.txt`
records 41 tests with 20 failures and two errors (including subtests);
`admission-runtime-green.txt` records all 41 passing. The earlier setup-only
failure is retained separately as `admission-runtime-setup-red.txt`, not counted
as the behavior RED. The production-branch tests relocate only path guards into
a temporary repository; they do not call production execution. Their solid PNGs
are generated at the metadata dimensions, not native or browser observations.

### Proof chronology

These three snapshots are additive evidence, not a rolling test-count file:

1. [`synthetic-check.json`](synthetic-check.json): original 16-test reading,
   restored byte-for-byte from `17e2fccc888a0ae5f6252d3cac73705a4245d86b`.
2. [`synthetic-check.durability.json`](synthetic-check.durability.json): verbatim
   24-test snapshot from `33a8954fc157925e3de7918ce7567fee5941ef85`. That commit
   had overwritten the original pathname; this correction preserves both
   observations explicitly. Neither historical snapshot is to be overwritten.
3. [`synthetic-check.admission-runtime.json`](synthetic-check.admission-runtime.json):
   this 41-test proof, inventory admission counts and implementation hashes.

[`evidence-index.json`](evidence-index.json) records full hashes and provenance
for the three snapshots and their RED/GREEN transcripts.

One separate test exercises the real subprocess backend's command construction and output/provenance parsing using a substituted
process; **it does not launch Chromium**. No native payload, archive Reader,
native bundle, matrix CLI, browser or actual web capture was used in G0.

## Freeze contract for G1

The entry points are Python APIs, intentionally not an `expose` CLI that can be
run accidentally. Production cannot take a log path or an injected backend.
`run_synthetic` cannot accept a production manifest and must use paths outside
the evidence repository; it does not open or inspect the production receipt.

1. Commit the renderer, its numerical candidates, its configuration, its scorer
   and every prediction payload. Build `@vitrea/policy`, copy every generated JS
   module under `packages/policy/dist/` into committed evidence snapshots, and
   declare their `runtimeArtifacts` mapping as described below. Source-only
   freezes and missing/stale compiled artifacts are refused. A candidate is an
   implemented surviving **composite** (body/stroke operators and their held surroundings), not a
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
  Supply every **declared AND archive-admitted glass** cell across calibration,
  validation and holdout, including glass placements the web runtime cannot pose.
  No-glass references and opaque controls are not prediction cells. The numerical
  instrument owns each prediction's inner shape; it must not be empty or contain NaN/Infinity. A prediction is a forward
  output, not a path or digest substituting for its payload.
- `rendered-predictions.json`: `{"cells":{"profile/scene":{"png":"path.png",
  "projection":"path.json"},...}}`. Supply every **web-plannable, admitted**
  glass cell across all three roles. Each PNG is decoded and dimension-checked. Each
  projection is finite JSON from the same `project` routine used during exposure.
  Under clause 11 / charter v2.3, held-out **web** predictions are produced
  **blind before exposure**, solely from public declared backdrop and geometry
  through the committed generated-backdrop bundle: never from a native fixture
  or archive payload. Freeze hashes those predictions while native holdout stays
  unopened. The receipt recaptures and requires byte/projection equality **before
  native held-out scoring**; mismatch or nondeterminism fails and spends the
  exposure. “Inside the receipt” governs every Apple held-out pixel read, not the
  blind web renders. No missing PNG can be replaced by a numerical output.
- `survival.json`: `{"numerical":{"profile/scene":true,...},
  "rendered":{"profile/scene":true,...}}`. These are the scorer's admission
  summaries for every **admitted** calibration/validation cell in the respective scope;
  A `true` means every admitted constraint is met: measured channels satisfy
  max(1,bar), rail channels satisfy their hard one-sided bounds, and deficient
  bins are excluded and counted under X31 v2.2. `false`, missing, extra or holdout
  entries refuse freeze. Include the detailed
  survival/veto reports in `instruments` too: the booleans are admission, **not a
  substitute for the charter's per-channel/bin, seven-repeat proof**.
- The configuration is
  `{"fixtures":"path/to/generated-web-backdrops","runtimeArtifacts":{
  "packages/policy/dist/index.js":"packages/calibration/results/.../policy/index.js"},
  "candidates":{
  "composite-e3-m1":{"profiles":{"profile-key":{"material":"active.json",
  "receded":"receded.json"}}}}}`. Every candidate needs all rendered profiles.
  Both material document bytes are frozen. These are scratch candidate documents,
  not resealed shipped profiles. The fixture directory is a **generated web
  backdrop bundle**, not the native archive: its `manifest.json` contains only
  optional `schema` and `backgrounds` (`"background-id@1x":"relative.png"` and
  `@2x`). Every required background PNG is frozen, decoded and dimension-checked.
  G1 supplies these non-captured sRGB rasters; this runner never runs the native
  harness to create them or mounts a native capture tree.
- `runtimeArtifacts` in the configuration maps each actual repo-relative policy
  JS module path to its committed evidence snapshot path. Include **every** `.js`,
  `.mjs` or `.cjs` module recursively under `packages/policy/dist/`, including
  `index.js`; the one-entry example above suffices only for a one-module build.
  Snapshots must live under `packages/calibration/results/`. Freeze checks their
  committed bytes against the actual build, hashes the snapshots into `files`,
  and copies the mapping into the manifest and receipt renderer record. This
  separately identifies what executed; it does not claim the build was derived
  from the frozen source or that a lockfile attests generated workspace output.
  A synthetic subset may omit the mapping; if supplied, it receives the same
  inventory and byte checks. Production may never omit it.
- `scorer.py`: the committed scoring module described below. `instruments` lists
  any other imported code, numerical inputs, resolved-material sidecars, spatial
  findings, veto reports and configuration that determine predictions or scores.

`files` in the manifest maps **every committed input path to its full SHA-256**;
actual generated modules are identified separately by `runtimeArtifacts`. In
addition, the runner automatically freezes runtime package sources (including
policy source even though Vite executes its compiled build),
calibration web/scripts/src, package manifests, workspace/lock files, and all
Python sources in the W39 G0/G2 and W41 G0 instrument trees. Added or deleted
source files are changes too. `revision` names the source commit;
`boundarySha256` and `runnerSha256` name the executing Python boundary;
`scenes`, `split`, `generation`, `sourceFiles`, `numericalCells` and
`renderedCells` pin the membership and source inventories. The sole production
`generation` is W39's inventory SHA
`58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61`.

Production always binds the committed metadata file
`packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting/archive/inventory.json`
as `inventory` and in `files`, checking its exact fixed SHA before reading
`entries[].cell`. No referenced payload is opened by freeze. Both prediction
membership and survival membership derive from declared glass **intersected with
that admission**, not from every declared phase probe:

| Scope | Declared | Admitted | Calibration/validation | Holdout | Excluded |
| --- | ---: | ---: | ---: | ---: | ---: |
| Numerical | 704 | 648 | 576 | 72 | 56 |
| Rendered | 608 | 600 | 536 | 64 | 8 |

`excludedCells.numerical` and `.rendered` explicitly map each omitted cell to
`not admitted by fixed archive inventory`; all of these are calibration phase
probes. The split is unchanged; standing sheets deliberately retain the broader
declared scope. Exposure selects holdout from the admitted manifest lists.
Synthetic subset manifests have `inventory: null` and empty exclusion maps;
they do not acquire the fixed archive's production authority.

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
and `captures` (candidate ID → cell → **fresh capture path**). Nested manifest,
candidate and capture mappings are detached deep copies, not the runner's trusted
comparison state. A callback must not mutate them; the runner refuses observed
mutations. Capture backends likewise receive a detached manifest. The scorer must
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
exactly. Then the native scorer runs. Frozen inputs and the original manifest
identity are reverified after capture and after scoring, and the fresh PNGs are
rehashed against independently held capture-time hashes after scoring. Actual
policy build bytes and module inventory are verified before `begin`, immediately
after every capture/project callback, and after scoring (after the score has been
durably retained). An added module, removed module or stale build refuses the
attempt, even if every frozen prediction PNG would otherwise match.

Immediately when `score` returns valid JSON, the runner writes the **full returned
report** (all bins/channels/repeats, not just passing summaries) to the runner-owned
`<receipt-stem>-scores.json` in the receipt's own directory. For production this is
`wave-identification-receipt-scores.json` beside the inherited W39 receipt. It is
created exclusively, never overwritten; both file and parent directory are fsynced
**before** callback mutation checks, frozen-input checks, or score aggregation.
Its `status: "scored"` records a returned observation, not an accepted verdict. It
binds the original manifest SHA-256 and fresh capture paths with hashes observed
before scoring. If an image is subsequently changed, that original hash remains
the witness; the verdict refuses completion rather than relabeling the new image
as the scored capture.

`result.json` in the output directory is the separate verdict, also written and
fsynced before W39 appends `complete` or a caught failure appends `failed`. A
successful verdict retains the scores, coverage and capture inventory. A failed
verdict retains the full returned scores when available, original manifest
identity, capture inventory and the exception type/reason. Both reference the
authoritative score record by path and SHA-256 when it was persisted. A scorer
exception records failure without a `scores` field: no return means no invented
reading. The authoritative report survives aggregation or freeze failure and even
a process killed before the verdict can be written. Scores are the authoritative
record of that exposure, **never re-scored by a second exposure**.

A failure after `begin` appends `failed` and consumes the entire exposure. An
uncatchable interruption can leave the durable score record without a verdict or
terminal receipt event; it still follows inherited W39 lock/spent semantics and
permits no retry. Preflight mutation,
missing candidate payload or incomplete frozen coverage refuses before `begin`.
Once spent, a changed candidate cannot obtain another attempt. No path here
changes the inherited W39 source, declaration, split or protected evidence.

## Limits and integration stops

- This is the same **procedural**, not hostile-code security boundary as W39.
  Committed scorer code is trusted to implement the declared statistics, use
  guarded Readers and list transitive inputs. The runner checks its outputs and
  authority lifecycle; it is not a Python sandbox or a second numerical solver.
- The explicit policy snapshot binding attests those executed workspace bytes,
  not their derivation from source. A source/lock freeze does not attest other
  installed dependency bytes or the GPU/OS.
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
