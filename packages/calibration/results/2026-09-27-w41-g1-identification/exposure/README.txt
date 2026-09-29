W41 G1 — endpoint-scoped exposure instrument (additive version 2)
===============================================================

Decision Log 7, clauses 2/11, X26, §5.192. This directory is an instrument,
not a candidate, browser measurement, native reading or production exposure.
G0/exposure remains the original all-endpoint instrument and evidence. Its
README/schema/runner/proofs and bounds-declaration.txt are not rewritten.
This separately versioned runner retains G0's single W39 receipt, admission,
source/runtime binding, blind recapture equality and durable scores-before-verdict.

Ruling provenance
-----------------
The following is the ABRIDGED parent relay supplied in this task, not a verbatim
primary quote. The original parent ruling is recorded by the coordinator in §5.192:

'partial-endpoint adoption is allowed ... Carry the light-inactive body to step5 ... operator enabled in light receded scratch document, at identity(zero gate) in other3 ... E3 leaf candidate(3 parameters against6), EH6 recorded equivalent survivor. Runner keeps scoring complete admitted membership across all endpoints, but closure tested on claimed strata held-out cells(1x/2x light inactive); unclaimed strata reported as "not claimed (identity)" with scores shown, never failures of candidate and never passes; freeze records claim scope. Per-bin veto and rendered check run every web-plannable cell; at identity operator renders baseline, so unclaimed cells must read byte-identical to baseline and equality itself is a test.'

This changes the endpoint scope of a candidate's claim, not the sealed numerical
rules. The declaration remains SHA-256
850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759.
All 648 numerical / 600 rendered admitted predictions remain required; 576 / 536
are calibration/validation and 72 / 64 are held out. Fixed inventory metadata,
not a caller allowlist, supplies admission. All 72 / 64 held-out scores remain.

Freeze and scorer integration
----------------------------
Use this sibling runner.py, not G0's. Its API is unchanged:

  freeze(root, wave, candidates, config=..., scorer=..., declaration=...,
         closure=..., instruments=[...])

Production declaration/closure still point to G0. The new manifest schema is
w41-renderer-exposure-2. Every candidate now supplies an additional committed
claimScope JSON path, for example:

  {"id":"body-e3-light-inactive", "parameters":".../parameters.json",
   "predictions":".../numerical.json", "rendered":".../rendered.json",
   "survival":".../survival.json", "claimScope":".../claim-scope.json",
   "identityBaseline":".../identity-baseline.json",
   "domainEvidence":".../capture-domain.json"}

The endpoint declaration is:

  {"endpoints":[{"colorScheme":"light","activation":"inactive"}],
   "numericalDomain":"uniform-backdrop",
   "renderedDeepDomain":"uniform-backdrop",
   "domain":{"policy":"nominal","variant":"regular","samplingBackend":"gpu-texture",
             "presence":{"identified":1,"intermediate":"unmeasured-linear-interpolation",
                         "zero":"exact-skip"}}}

body-e3-claim-scope.json is the committed light-inactive uniform-body declaration
for the intended E3 candidate. It is not itself a candidate freeze or authority to
expose. scope-membership-rendered-domain.json records its final metadata-only
membership reading; scope-membership.json retains the earlier numerical-only
structured-domain checkpoint and must not be mistaken for the final scope.

Both scales are automatic. Endpoint identity is derived from the profile's
colorScheme and the scene's declared state (rest -> active; inactive -> inactive),
never inferred by a candidate's cell names. Empty/duplicate/unknown endpoints,
per-cell selectors and scale selectors refuse. Even an all-endpoint candidate
must declare its scope; old manifests cannot acquire new semantics silently.

Numerical/rendered predictions keep G0's exact shapes and complete memberships.
Survival JSON retains numerical and rendered maps on every pre-exposure cell
(the structured numerical exception is distinguished below):

  claimed cell: true
  unclaimed cell: {"status":"not claimed (identity)","passes":null,
                  "score":{"status":"measured","passes":false,
                           "worstResidualCodes":25}}

The inner score is the actual reading, including misses; it may instead be a
valid censored observation. A true on an unclaimed endpoint is refused. Claimed
true retains every G0 survival/censor/bin/repeat obligation. Detailed survival
and transfer reports remain committed instruments, not replaced by booleans.
Survival also requires veto: {cell:true,...} for EVERY admitted rendered
calibration/validation cell, independent of endpoint claim.

The scorer still exports project(cell,png) and score(ScoreRequest). It receives
the complete admitted held-out numerical/rendered cell lists. Return raw scores
for every candidate/kind/cell, even unclaimed endpoints. Measured rows require a
boolean passes; censored rows require status UNMEASURED, reason censored,
passes:null, and boolean constraintsPass. All per-channel/bin/repeat evidence
stays in those rows. Every rendered row additionally requires vetoPass:true,
including unclaimed rows. The scorer uses the full blind shipped baseline for
the veto; include that payload map and its provenance in instruments.

The runner never asks the scorer to hide an unclaimed miss. It preserves raw
scores durably, then produces assessments whose unclaimed entries are explicitly
{status:"not claimed (identity)",passes:null,score:<raw reading>}. Such cells
count toward neither claimed passes nor claimed measured coverage. Claimed
censor semantics remain exactly G0's: an uncensored or rail failure fails closure;
a satisfied censored cell counts as censored, not measured or passed.

Coverage fields distinguish the denominators: measured/censored/total/fraction
are CLAIMED membership, scoredTotal is COMPLETE membership, notClaimed is the
remainder. For light-inactive only, numerical heldout is total18/scoredTotal72/
notClaimed54; rendered is total16/scoredTotal64/notClaimed48. Censoring may lower
measured, never those memberships. claimScopes travels in the manifest, receipt,
durable full score record and final result.

Uniform deep-body claim is not the shader enable domain
------------------------------------------------------
The parent's later clarification limits E3's numerical identification to uniform
backdrops, not its shader application. numericalDomain="uniform-backdrop" is
therefore explicit and mandatory. The runner derives numerical and rendered-deep uniformity solely from the
public scene's background metadata: background.kind == "solid". No candidate
cell/colour/scale allowlist, measured residual, or fabricated success chooses it.

The six structured light-inactive calibration cells remain numerical members and
retain their S0 diagnostic deep scores (apply E3 per local reference pixel, then
take the declared median). Their numerical survival entry is:

  {"status":"not claimed (structured backdrop)","passes":null,
   "score":{"status":"measured","passes":false,"diagnostic":"S0", ...}}

These are not numerical admission and do not fail the uniform law. The detailed
S0 evidence belongs to the scorer/instrument; the runner requires the explicit
diagnostic marker and preserves its actual reading. An artificial true is refused.
There are24 numerical structured cells total (6per endpoint), not24 additional
unclaimed cells, and16 rendered structured cells total (4per endpoint). Other
endpoints remain "not claimed (identity)" with their scores shown; endpoint
identity takes precedence over the structured-backdrop diagnostic label.

No structured heldout cell exists in the sealed bed, so the72/64 heldout scope,
18/16 claimed light-inactive membership, and censor rules do not change. The later
confirmed parent ruling (rendered-domain-ruling.txt) also limits RENDERED DEEP
absolute closure to uniform backgrounds, recorded independently as mandatory
renderedDeepDomain="uniform-backdrop". The four light-inactive structured rendered
calibration cells retain the actual rendered deep score under
"not claimed (structured backdrop)" with passes:null, not fabricated true. That
reading is a real rendered diagnostic, NOT the numerical S0 prediction; the S0
marker is required only on the structured NUMERICAL diagnostic.

Every structured rendered cell remains a member of the sampled SHADER domain and
of the W38 worsening veto. The veto binds every admitted bin, channel and repeat,
INCLUDING the structured deep body: worsening its baseline residual by more than
one code fails. On claimed uniform cells, absolute max(1,bar) AND veto both bind.
The shader does not detect uniformity or switch off on gradients. identityBaseline
still covers450 endpoint-identity cells, NOT those four enabled structured cells.
All600 rendered memberships, all536 calibration/validation veto rows and the64
blind heldout rows remain. This creates no spatial claim or leaf; spatial holdout
remains deferred.

This version's numerical adapter is for the uniform-body candidate. That is an
integration limit, not a change to the scientific charter. Stroke identification
continues under its sealed full budgets; if it yields a survivor, this SAME G1 wave
may need a separately declared stroke/all-backdrop adapter before the one shared
freeze/exposure. Nothing here authorizes exposing E3 before all candidate
identification and rendered checks finish; no second receipt is available.

Domain: observations and authored facts are different evidence
------------------------------------------------------------
A subsequent parent ruling requires the fixed domain shown above. It is mandatory
for every candidate, never an optional filter or permission to remove a cell.
The claim covers nominal accessibility, regular glass, actual sampled backdrop
texture and presence1 only: not RT, IC, forced-colors, clear glass, fabricated DOM
or absent sampling. Intermediate presence is unmeasured linear interpolation;
presence0 is an exact skip. For E3 the operator consumes the existing post-
refraction/blur sample and replaces the old tone solve/retention/black branch at
full presence on the claimed endpoint, before author tint, with the rim unchanged.
The operator implementation/proof belongs to its frozen source instruments;
this runner binds the domain and its evidence, not a second shader implementation.

Each candidate's domainEvidence path names committed JSON:

  {"attestation":".../domain-attestation.json",
   "cells":{"profile/scene":{"descriptor":<complete decoded cell__webgpu.json>,
                              "report":<complete decoded report__webgpu.json>},...}}

Exactly ALL600 rendered cells are required, including unclaimed and blind heldout
cells. These are the actual capture records, not reconstructed booleans. The
runner checks profile a11y=standard, matching scene IDs, actual WebGPU/gpu-texture,
the texture request with no fabricated author level, all actual group sampling
states, and all four resolved accessibility flags false. The validator follows the actual producer wrapper: page observations live under
report.page; capture scheme and material-file provenance are top-level. Frozen
and fresh records are matched to their profile's dimensions, requested/actual
scale, driver/actual scheme and the configured material/receded document hashes
and patches. Candidate receding preserves the producer's real posing semantics:
the root remains active while an inactive scene applies the candidate receded
patch and its exact deep merge into the page material. It does not demand an
inactive root for that deliberately root-active capture path. The same validator
runs on every fresh heldout capture inside the receipt. Fresh descriptor/report bytes
are hashed into the capture record and rechecked after scoring. A missing or
out-of-domain record refuses rather than shrinking admission.

The producer does NOT report SurfaceReport.variant or presence. The coordinator
explicitly authorized source-derived provenance for those facts, not inventing
runtime observations. The committed attestation therefore has this shape:

  {"basis":"source-derived","variant":"regular","presence":1,
   "effectivePresenceBasis":"Explain the complete registration/default/packing chain.",
   "limitations":"These two facts are source-derived, not observed runtime fields.",
   "sourceChain":[{"path":"packages/calibration/web/scene.ts","sha256":"...",
                   "claim":"Explain the regular registration and omitted channels."},
                  {"path":"packages/.../src/...","sha256":"...",
                   "claim":"Explain how the omitted channel resolves/executes as one."}]}

Every source link must be in the frozen source inventory with its exact SHA256,
a nonempty factual claim, and no duplicate path. Registration and at least one
runtime source are mandatory; missing/stale source evidence refuses. The human
source audit must actually close the chain, not stop at 'requested default'.
Relevant current source locations include scene.ts's regular registration,
renderer-webgpu/src/instances.ts's materialization packing/default and WGSL field/
optics presence use, plus the actual IDLE_CHANNELS definition/producer paths.
This is trusted committed source-audit evidence, not mechanical proof of arbitrary
TypeScript semantics. The runtime policy/sampling observations remain mandatory
and are not inferred from those authored facts. No new report field is claimed.

Identity is an artifact comparison, including blind holdout
----------------------------------------------------------
identityBaseline is a committed JSON {"cells":{cell:{"png":"repo-relative.png",
"projection":"repo-relative.json"},...}}. It must cover EXACTLY the unclaimed
rendered cells across ALL roles. Freeze opens and dimension-checks every PNG,
requires identical PNG bytes to the candidate and equal projection JSON, and
hashes both baseline and candidate payloads. identityEquality in the freeze
records each role, both source paths and both PNG/projection hashes. Hash-only
promises to an uncommitted scratch capture are insufficient.

For the light-inactive claim this is 450 identity cells: 402 calibration/validation
and 48 heldout. The source baseline captures stay in scratch; content-addressed
committed evidence snapshots supply payload bytes. Include baseline capture
manifests, source provenance, preparation and projection instruments in instruments.
The baseline worker's committed-payloads.json supplies calibration/validation;
the coordinator owns the distinct blind heldout shipped-baseline extension.

Heldout identity requires NO native opening and NO membership narrowing. Both
shipped baseline and candidate heldout web predictions are rendered blind from
the public declared generated-backdrop bundle under clause11 v2.3. Freeze proves
candidate==shipped baseline before the receipt. Inside the one receipt, fresh
candidate recapture must equal frozen candidate byte-for-byte and projection-for-
projection before the native scorer runs; therefore fresh==baseline transitively.
An absent blind baseline refuses freeze. Nondeterminism spends the one exposure;
it does not authorize retry, exemption or a smaller heldout set.

Binding and safety
------------------
The new source inventory adds all Python files in the G1 instrument tree to the
inherited W39/G0/runtime source inventory. The G1 schema itself is hashed into
files. The committed claimScope, baseline manifest and every referenced baseline
payload are also hashed. Added imported source, changed schema, changed claims,
changed baseline bytes or changed compiled policy inventory refuse verification.
The original generation and receipt path remain unchanged. Production has no
injected backend, alternate receipt or retry; synthetic mode cannot authorize
the archive. Every returned score is still fsynced next to the spent receipt
before aggregation and retained even on claimed failure or process death.

The scorer module is imported only INSIDE the already-begun receipt. Therefore a
scorer's Python/package-version refusal can spend the exposure before projection
or native pixels. Run a side-effect-free interpreter/package-version probe before
run_production in addition to the scorer's own fail-closed runtime pin. Do not
pre-import the scorer to perform that probe: importing it outside authorization
would break the guarded loading contract. This instrument does not attest the
bytes of installed Python dependencies; use the scorer's declared runtime.

This remains a procedural, committed-code boundary, not a sandbox or an
independent implementation of the scientific scorer. Trusted instrument code
must retain seven repeats, exact bins, censor constraints, population exclusions,
and source provenance; supplying a summary does not relieve that obligation.
No test here opens an archive payload, production receipt or browser.

Tests
-----
  python3.12 -m unittest discover \
    -s packages/calibration/results/2026-09-27-w41-g1-identification/exposure \
    -p 'test_*.py' -v

The original 41 G0 regression behaviors are rerun against the G1 copy with the
new mandatory declarations. New regressions use temporary Git repositories and
synthetic solid PNGs, with public W39 scene/split/inventory metadata only.
claims-setup-red.txt is a setup error, not behavioral RED. claims-red.txt is the
original missing-scope behavior run (including expected relocation failures of
the unchanged G0 production path). veto-red.txt independently proves the missing
unclaimed-rendered-veto rejection. claims-attempt-1.txt records intermediate test
failures, not success. Later numbered evidence remains additive. claims-green.txt is a failed attempt
with one stale expected score shape; claims-green-2.txt records 53 passing tests
before the domain requirement. domain-red.txt proves missing mandatory domain was
accepted before implementation. domain-green.txt records all58 tests passing
after explicit domain binding. uniform-domain-red.txt proves the missing explicit
uniform numerical domain; uniform-domain-green.txt records60 passing tests after
that addition. These are checkpoints: independent review then found the actual
producer report wrapper and frozen record/profile binding needed corrections.
The fix wave adds its own producer-shaped tests/evidence; earlier green tests are
not relabeled as proof of those previously untested integrations. These files are
observations, never overwritten.

Final bounded fix wave
----------------------
Independent reviewer-high found two actionable defects at the earlier checkpoint:
actual producer report nesting and frozen profile/document association. review-1.json
records the incorrect verdict; these were not dismissed as debt. A separate bounded
worker supplied producer-shaped RED/GREEN regressions and fixes. The parent's later
structured-rendered-deep ruling has its own RED/GREEN evidence, not a relabeling of
the earlier numerical-only checkpoint.

fix-wave-producer-red.txt / fix-wave-producer-green.txt cover the genuine report
wrapper. fix-wave-associations-red.txt and the two association GREEN transcripts
cover profile, scale, scheme, pose and document substitutions, including nested
patch merging and the root-active candidate receded pose. The association
attempt-1 transcript records two /var path-alias setup errors, not scientific
failures. fix-wave-rendered-deep-red.txt catches the missing explicit declaration
and rejected structured-rendered diagnostic; fix-wave-rendered-deep-green.txt is
the full64-test passing checkpoint (synthetic only).

The suite proves instrument behavior, not an actual browser/native integration.
No production candidate freeze, exposure or capture is supplied by this directory.
A final independent scoped followup and the freeze1818 result are recorded beside
these checks before the instrument's scoped commit.

The scoped followup closed both original findings and verified the rendered-deep
scope. It found one additional narrow producer edge: an empty configured active
patch is not injected and the page reports explicit null, while an inactive
candidate still reports the actual merged object. review-2.json records that
finding. The bounded worker corrected only that convention and added the
producer-shaped empty-active-patch RED/GREEN regression; missing fields and wrong
empty/null substitutions are refused. fix-wave-empty-active-patch-green.txt is
the final full65-test passing suite, not a rewrite of the earlier64-test reading.

review-3.json closes that final finding: the independent targeted regression
passed and no material finding remained within the reviewed changes. The review
loop stops here; no broad repeat or real capture claim is implied.

Raw unittest failure transcripts retain their emitted trailing whitespace. A
whole-directory git diff --check reports those transcript lines; source, schema,
JSON evidence and this README pass the scoped whitespace check. The raw evidence
is not normalized to make a formatting check quiet.
