W41 G1 — E3 light-inactive candidate preparation (c9a §5.192)
============================================================

This directory prepares one body candidate, not an exposure or a rendered result.
The coefficients are the unchanged light-inactive E3 entry of
body/report-1/spatial-selection.json. EH6 remains an equivalent survivor, not a
second leaf. No coefficient is fitted here. The other three endpoints are at
identity: their numerical readings use the already-proved shipped H2 forward law
and its resolved-material sidecar. Those readings are NOT claims of E3 accuracy.

Claim and runtime domain
------------------------
The claim is the light-inactive endpoint, both scales, uniform backdrops. Shader
enabling additionally requires nominal accessibility policy, regular glass,
actual gpu-texture sampling and full presence. Intermediate presence is unmeasured
interpolation; zero presence skips exactly. The numerical prediction describes
the body's deep statistic, not the unchanged rim or other boundary contributions.
The enabled shader may draw on structured inputs, but this archive has no
structured holdout and establishes no spatial law.

The coordinator's 2026-09-27 clarification is preserved verbatim in
parent-ruling-rendered-structured.json. Numerical structured deep scores use S0:
apply E3 per pixel to each guarded local noGlass reference, THEN take the declared
deep median. They are "not claimed (structured backdrop)", never numerical
admission. Actual rendered structured deep max(1,bar) scores are likewise retained
as "not claimed (structured backdrop)" and labelled "rendered structured deep",
NOT S0. The W38 worsening veto remains binding there, including the DEEP BODY,
every admitted exterior/interior bin, every channel and all seven repeats. A
structured body median worsened by more than one code fails that veto. Claimed
uniform rendered deep must satisfy both max(1,bar) and the veto. Other endpoints
retain raw misses, have the same binding veto, and must be byte-identical to the
shipped baseline under the runner's identity check. All cells remain in the tables.

Interfaces
----------
scorer.py exports the G1/exposure runner's unchanged callback pair:

    project(cell: str, png: pathlib.Path) -> JSON
    score(request: runner.ScoreRequest) -> JSON

project delegates to baseline/baseline.py::project: the same supplied paths,
deep masks, bins and public-raster strip, with no native Reader or pixel read.
Import and forward projection do not need SciPy. runtime.json pins Python 3.12,
NumPy 2.3.5 and Pillow 12.3.0; project, score and preparation refuse a different
runtime before reading images. This is the existing pure-forward environment,
not the separate fitting environment. The eventual runner must be launched with
this runtime; matching Python alone does not establish matching projection bytes.
IMPORTANT: the runner imports the scorer only INSIDE the active receipt. A runtime
mismatch discovered there spends the exposure. Before any eventual run_production,
run a separate version-only probe importing sys, json, NumPy and Pillow (NOT the
scorer), and compare {python: list(sys.version_info[:2]), numpy: numpy.__version__,
pillow: PIL.__version__} with runtime.json. This external preflight changes no
runner authority and does not authorize any exposure.

score checks request.authorization before constructing the holdout Reader, then
passes that same authorization to request.wave.reader. Every crop and its embedded
noGlass reference comes through that guarded Reader. The whole ~/vitrea-w39 tree
is denied; only the fetched, hash-verified archive cache is eligible. The fixed
inventory generation is checked, including by the token, and no alternative
receipt path, exposure, retry or production entry point is added here.

The callback requires all 72 numerical / 64 rendered held-out identities from the
fixed public admission metadata. The numerical scope includes the native-only
grey-255 bottom placements. It returns exact candidate/kind/cell maps, with full
member/channel scores, all seven admitted normal repeats (even when repeat states
are identical), populations, bars, hard rail deficits and statuses. It scores the
NEW request.captures PNGs, not frozen numerical data or projections. The complete
raw rendered instrument output, exterior bins, interior comparisons, straddling
diagnostics and full veto records are retained. Only deep body constraints affect
the body's accuracy summary; edge absolute misses remain diagnostic because this
candidate claims no stroke. Edge/deep worsening still binds independently.

Deep populations below four are excluded and counted, not replaced with zero
error. A native value <=5 or >=250 is a one-sided rail; an exact rail violation
is binding even if another channel is measured. Any rail-containing body cell has
status UNMEASURED/reason censored with constraintsPass retaining every required
uncensored and rail comparison. It never contributes measured held-out coverage.
The runner, not this callback, wraps unclaimed raw results and counts coverage.

Frozen parameters must contain:

    {"body": <the complete E3 family/endpoint/neutral/coefficients object>,
     "shippedBaseline": "<repo-relative full-600-cell shipped baseline map>"}

The shipped baseline map uses cells[cell] = {png, pngSha256, projection,
projectionSha256}; the parameters point by default to candidate-e3/shipped-baseline.json.
This file does NOT exist until real frozen baseline captures are available.
Every baseline PNG, projection, map, provenance, imported source and numerical
sidecar must be included in runner.freeze(..., instruments=[...]). The runner
already inventories W39/G0 source trees; prepare.source_inputs() identifies the
additional G1 and numerical inputs. No pathname or hash substitutes for PNG bytes.

Preparation commands (Python 3.12; paths shown relative to this directory)
-----------------------------------------------------------------------
These commands are exclusive writers: use a NEW output directory for a new
reading, retain old evidence, never overwrite it.

    python3.12 prepare.py public public-1
    python3.12 prepare.py numerical-calval public-1/numerical.json calval-1

public uses PUBLIC metadata only for all 648 numerical cells: 576 calibration /
validation and 72 held out. All 72 held-out backgrounds are uniform. The 24
structured calibration/validation predictions use local public-raster pixels then
the deep median and carry a diagnostic limitation. numerical-calval reads only
calibration then validation through guarded Readers, never constructs a holdout
Reader, and recomputes structured diagnostic predictions from each guarded state's
local noGlass pixels. Both frozen-public and native-reference diagnostic residuals
are retained. It writes numerical-admission.json, NOT a composite survival file.

Only AFTER actual captures exist, a coordinator may use:

    python3.12 prepare.py baseline-map shipped-baseline.json
    python3.12 prepare.py render-calval candidate-captures.json shipped-baseline.json rendered-calval-1

baseline-map validates both frozen shipped capture manifests and their hashes,
checks projection equality in the pinned runtime, and snapshots external calval
PNGs as repository-relative content-addressed payloads. Existing committed blind
payload references stay intact. The union must contain all 600 rendered cells.
render-calval accepts a cells map with png and pngSha256 for every 536 admitted
calibration/validation candidate frame. Missing maps/images are an integration
stop, never a fabricated survival result. It creates no browser or capture. It
retains full raw score/veto reports and separate rendered admission and identity
byte failures. A coordinator must combine these with the numerical report and
runner's identity/domain checks; a failed veto or identity check bars the freeze.

Freeze also requires the candidate's actual rendered predictions/projections,
identityBaseline (exactly 450 endpoint-identity cells across all roles), domain
reports, source-derived domain attestation, scratch documents, actual runtime
policy snapshots, and the final claimScope from G1/exposure. This directory does
not fabricate any of them. The complete 600-cell baseline, not the 450-cell
identity subset, is necessary for the veto on the claimed endpoint as well.

Verification and limits
-----------------------
The initial tests were written before scorer.py/prepare.py existed; their RED
transcripts explicitly show missing implementation. Green tests exercise fixed
E3 continuation and gain, all648 metadata membership and members, S0 pixel-before-
median ordering, hard rails, seventh-repeat failure, deep populations, absolute-
before-mean veto, explicit exclusions, runtime checking, import/project with SciPy
and native Reader forbidden, synthetic archive envelopes, authorization refusal,
and actual fresh synthetic PNG changes causing the structured deep veto to fail.
These are synthetic tests, not browser captures or native held-out readings.
Additional review fixes have their own RED/GREEN transcripts. No synthetic receipt
or payload grants production authority. Reviewer-high reviewed the source boundary;
its two integration/reporting findings were sent to a separate fix worker.

No browser, renderer invocation, runtime/material-document edit, holdout opening,
receipt, freeze or production exposure was performed by this preparation worker.

Completed preparation evidence (2026-09-27)
-------------------------------------------
public-1/numerical.json contains all 648 admitted public predictions (504
calibration, 72 validation, 72 unopened holdout), with every glass member retained.
public-1/parameters.json names the unchanged E3 coefficients and the pending
full shipped-baseline map. Provenance lists source hashes and zero native reads.

calval-1/scores.json.gz retains every raw numerical comparison for all 576 admitted
calibration/validation cells and 592 glass members. calval-1/numerical-admission.json.gz
is only the numerical half of future admission, not an exposure-ready survival
artifact. All 138 claimed uniform cells (140 members) meet their constraints:
136 are measured and two are censored with constraints satisfied; the worst
uncensored residual is 0.8323554076898176 code. Six structured claimed-endpoint
cells (eight members) retain S0 diagnostic scores, worst 0.9090909090909065 code;
their small residual is not numerical admission or a spatial closure. All 432
identity cells (444 members) retain actual shipped H2 scores, including misses
up to 125.29671418140109 codes; they are neither passes nor failures of E3.
outcome.json gives the exact worst cell/channel/repeat witnesses.

Both reviewer findings are fixed by the separate worker, with failing regression
proof then green in reviewer-high-red.txt / reviewer-high-green.txt. The complete
synthetic candidate suite has 25 passing tests. No rendered calibration scores,
rendered predictions, baseline map, composite survival flags or freeze manifest
were generated: actual baseline/candidate PNGs remain the next dependency.

The complete numerical admission payload is stored losslessly as gzip rather than
395,302 lines of duplicated raw-score JSON. calval-1/admission-storage.json pins
both original and stored SHA-256/byte counts; decompression reproduces the exact
prepare.py output. This changes storage only, not any number or admission.
