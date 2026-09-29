W41 G1 — guard-only source transition, not a repeated native measurement
======================================================================

The historical E3 public-2/calval-2/rendered-calval-1 readings and the complete
candidate-capture/attempt-1 seal name runner02ed4421, committed at9b6d1bf7. Their
source witnesses remain exactly as recorded. After candidate, CSS and canonical
capture/scoring source barriers were released, the reviewed X6guard commits were
applied as a47bf1ca and16977f4b, producing runner5ae591ad. This directory adds the
source-transition proof under claims§5.192; it does not relabel old measurements
as executions of the new guard.

bridge.py pins both exact runner digests, compares all preexisting functions,
classes and module-level statements, and admits only the reviewed guard changes:
freeze's required observer inputs, CaptureRequest, capture_web and _run, plus the
new X6 helpers/imports. Membership, numerical/scoring helpers, domain validation,
claim/censor/veto assessment, schema and material inputs are not changed. Every
historical source witness other than the explicitly named runner must still match
current committed bytes. The old capture's191source frontier and all its sealed
inputs are checked; all4212frozen capture artifact hashes and committed Git blobs
are verified without resealing or running the old driver's verifier against a new
source generation. The old driver.verify intentionally rejects that generation
change; it is not weakened or rewritten.

The instrument reproduces all648public predictions in memory under old/new runner
modules and compares them with the unchanged committed bytes. It checks unchanged
648/600admission (72/64holdout), and runs the final runner's domain validator on all
600existing capture reports plus the source-derived presence attestation. It does
NOT call runner.freeze, run_production, any Receipt, scorer.score, a native reader,
or a capture command. Public prediction execution has native-reader entry points
replaced by explicit refusals. Retained native score reports are hashed as existing
artifacts, never remeasured against the native archive.

The optionally named tier-coherence test-only wording commit is classified outside
runtime/capture source inventories and bound by before/after hashes. Its separate
worker review establishes that the test strings/comments changed, not runtime CSS
or assertions; the source bridge does not infer production CSS parity. The report
names the actual HEAD and refuses if HEAD changes during verification. It is not a
final-wave source inventory: that freeze still waits for every stroke verdict and
all final inputs. Concurrent uncommitted work outside these inputs is not adopted.

Run only after committing bridge.py and its synthetic tests:

  PYTHONDONTWRITEBYTECODE=1 python3.12 bridge.py \
    --text-fix-ref 5d492c15023ef475d729ef68397589e53dbf44fd \
    --out reading-1.json

Output is exclusive and fsynced. A rerun uses a new filename, never replaces a
reading. A failed verification must be repaired/recorded before using this bridge;
the historical evidence remains unchanged regardless.

The synthetic RED/GREEN proof rejects undeclared scoring/global/top-level changes,
a wrong old runner witness, any unrelated source or artifact mutation, and output
overwrite. Independent reviewer-high found no material findings in the instrument;
actual evidence verification is a separate subsequent reading. Primary regression
checks after applying the guard passed76exposure,25scorer and8preflight tests, all
synthetic. No runtime package or native fixture moved in this transition.
