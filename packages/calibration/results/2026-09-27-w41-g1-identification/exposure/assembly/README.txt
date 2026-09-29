W41 G1 — BODY-E3 input assembly from existing evidence only
=========================================================

This reducer prepares one candidate's reusable inputs under claims§5.192. It is
NOT a final-wave freeze, body-only exposure, new native reading or recapture. All
stroke verdicts and any composite-candidate requirements must be settled before
the wave's single final freeze/receipt. The runner/scorer/runtime are unchanged.

Inputs and reduction
--------------------
The complete600candidate web map and full600scorer shipped baseline retain their
original hashes and richer four-field records. New rendered.json and identity-
baseline.json contain the runner's EXACT two-key per-cell {png,projection} views.
Identity is selected by endpoint, not uniform-background claim:450cells including
48blindheldout. The four light-inactive structured rendered cells are enabled-body
diagnostics with binding vetoes, not identity cells.

Existing calval-2 and rendered-calval-1 full scores and original admission payloads
are streamed one top-level cell at a time, directly from their committed gzip files.
A cell's numerical raw reading remains intact. Its rendered compact score retains
all deep/member/seven-repeat/censor/state information and original status fields;
only rawRendered, interiorTransfer and the large veto array leave the duplicated
compact score. Those remain intact in the original full score report. Every cell
has a hash-bound JSON-pointer link to its full raw score and original admission,
plus a canonical SHA256 over each linked cell value. The separate evidence-links
file keeps the survival schema exact, without hiding details behind a bare flag.

The reducer checks all seven deep/veto repeats, rail coverage and summary agreement,
original admission equivalence, exact numerical576/rendered536membership, every
rendered veto flag, and current runner.aggregate assessment/coverage equivalence
between each complete raw cell and its compact form. Final aggregate coverage is
compared to the previously recorded rendered-calval strata result. Unclaimed raw
misses remain readings, never passes. Structured numerical readings retain S0;
actual structured rendered readings retain their own rendered diagnostic. Claimed
censored cells require constraintsPass:true and never count as measured passes.

survival.json is ordinary JSON with only numerical576, rendered536 and veto536
maps. Claimed admissions are true; unclaimed admissions retain their explicit
not-claimed wrapper and compact score. Full raw/admission.gz files are frozen
supplementary instruments, not decoded into a2.45GB duplicate survival document.
The streaming decoder rejects duplicate keys, nonfinite numbers, truncated data,
extra trailing data and score/admission membership differences. Each encoded JSON
key/value is capped at16,777,216decoded Unicode characters (inclusive; quotes,
escapes and internal whitespace count), with one character of delimiter lookahead.
This bounds malformed-input buffering rather than claiming an RSS limit. The
largest measured value in the four existing reports is8,627,814characters; all
576/576/536/536cells stream successfully under the limit. The sizing and malicious
stream regression evidence are preserved beside the tests.

Source/input integrity
----------------------
Historical identity starts from the exact transition/reading-1.json SHA committed
at5d7c37ee, not a newly accepted current hash. Its retainedArtifacts, original
source-witness document hashes, source maps and frozen capture/seal identities
are verified before reuse, with only the explicit02ed-to-5ae runner allowance.
Both the imported bridge.py and its test file are checked against bridgeSources
before importing the helper, and join the assembly-local input hash set.
All inputs must be committed regular files with matching Git blob bytes. Every
referenced web PNG/projection hash is checked; identity compares both payload
hashes; candidate PNG dimensions and all600domain reports are revalidated. The
complete captured file inventory is checked without running the historical capture
verifier against a different runner generation. The reviewed source bridge remains
a supplementary witness. The reducer refuses source/data drift during assembly
and names one sourceRevision; no prior evidence or seal is rewritten.

Run after committing the reviewed reducer:

  PYTHONDONTWRITEBYTECODE=1 python3.12 assemble.py --out <absolute-new-child-directory>

Output directory must be a new child of this assembly directory. It contains
rendered.json, identity-baseline.json, survival.json, evidence-links.json,
inputs.json (actual input SHA256s), instruments.json, candidate.json and summary.json.
The source files and all generated artifacts are committed before a later freeze.
Native-reader entry points are explicitly refused during this preparation.

Future freeze interface — NOT executed by this task
--------------------------------------------------
The candidate spec has id="body-e3" and points to public-2's unchanged parameters
and648numerical predictions, the new rendered/survival/identity views, the committed
body-e3 claim scope and existing candidate-capture/attempt-1/domain-evidence.json.
Its current runtime config is candidate-capture/attempt-1/runtime.json. The scorer
is candidate-e3/scorer.py; declaration/closure remain G0's unchanged files.

After ALL wave candidate decisions and final input commits, the coordinator may
include this spec in the complete surviving candidate list and merge runtime
configurations where necessary. Conceptually:

  runner.freeze(ROOT, runner.boundary.default_wave(), ALL_SURVIVING_CANDIDATES,
      config=COMPLETE_RUNTIME_CONFIGURATION,
      scorer="packages/calibration/results/2026-09-27-w41-g1-identification/candidate-e3/scorer.py",
      declaration="packages/calibration/results/2026-09-27-w41-g0-declaration/bounds-declaration.txt",
      closure="packages/calibration/results/2026-09-27-w41-g0-declaration/closure.json",
      instruments=COMPLETE_INSTRUMENT_LIST)

The E3 instruments.json contributes its complete retained evidence/payload paths;
it cannot authorize omitting another surviving candidate's evidence. A body/stroke
composite may need its own scorer/configuration, not blind reuse of this body-only
callback. The returned manifest must then be committed and externally preflighted.
Nothing in this directory calls freeze or writes/opens a receipt.

Review chronology
-----------------
review-1.json records three actionable findings at the original7-test checkpoint:
historical identity, imported-helper binding and malformed-input buffering. A
separate bounded fix worker addressed all three with behavioral RED/GREEN evidence.
fix-green-1.txt records14passing assembly tests; fix-bridge-green.txt records the
six unchanged bridge regressions passing. fix-value-sizing.json and
fix-retained-stream-green.json name the unchanged report hashes and complete
streamed memberships; these read saved reports, never the native archive. Actual
assembly remains a separate operation after committing the reviewed instrument.
