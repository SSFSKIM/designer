W41 external dry preflight — preparation, not exposure evidence
==============================================================

The scorer deliberately imports only after Receipt.begin. Its version guard is
therefore too late to protect the one exposure from an interpreter/package
mismatch. This separate script probes only NumPy/PIL and Python's major/minor;
it never imports the scorer. It first compares every manifest-pinned file to
HEAD and its frozen SHA256, including runner, inherited boundary, runtime.json
and this script. It then calls the existing runner.verify(..., 'production')
for full source inventory/revision, compiled runtime artifacts, domain evidence
and complete freeze reconstruction. No other receipt, token or Reader exists.

The runner import and verification were inspected: they read public scene/split
and inventory metadata plus committed WEB prediction/baseline/backdrop PNGs and
projections. They do not read native archive payloads or the production receipt,
import a scorer, launch a browser or run the renderer. This relies on the same
trusted committed artifact declarations as the runner: native pixels must never
be mislabeled as web evidence. Python bytecode writes are disabled here.

Run immediately before run_production, under the SAME interpreter/environment
and unchanged checkout/build. A success is a dated observation, not permission,
a receipt, or protection against changes made after it. Stop on nonzero; retain
the JSON beside exposure evidence and inspect its refusal. Never retry exposure
on the strength of this script. Dependency versions, not installed dependency
bytes, are attested. Python patch versions are not pinned by runtime.json.

From the worktree root, once the final production freeze has been committed:

  G1=packages/calibration/results/2026-09-27-w41-g1-identification
  python3.12 -B "$G1/preflight/preflight.py" \
    --manifest "$FINAL_COMMITTED_MANIFEST" \
    --evidence "$EXPOSURE_EVIDENCE_DIR/preflight-$(date -u +%Y%m%dT%H%M%SZ).json"

Both environment variables name actual paths chosen by the exposure owner; the
manifest pathname did not exist when this script was prepared. The evidence
directory must already exist, and the output file MUST NOT exist. Exclusive
creation refuses collisions instead of overwriting an earlier success/refusal.
Success and refusal both carry UTC start/finish times, manifest/runtime digests
when readable and committed, completed checks, and the error on refusal. An
unreadable/uncommitted input cannot earn a committed-byte digest claim.

Commit these files BEFORE constructing the final freeze: runner.sources includes
all G1 Python, including these tests. Include candidate-e3/runtime.json in the
freeze instruments. Any subsequent source edit requires a new pre-exposure
freeze, never a post-exposure repair of a frozen reading.

Tests (scratch Git repos and synthetic PNGs only):

  python3.12 -B -m unittest discover -s "$G1/preflight" -p 'test_*.py' -v

The initial tdd-red.txt shows the absent implementation. tdd-green-attempt-1.txt
records eight passing tests. The synthetic success test adapts only module loading
to the real runner.verify synthetic fixture; the production CLI has no synthetic
mode, backend override, alternate receipt or scorer import. Stale committed and
uncommitted instrument bytes, stale runtime bytes, each live version mismatch,
missing manifests and added source inventory refuse. Evidence replacement is
refused. Receipt/run_production calls are tripwires in the synthetic tests.
These are instrument tests, NOT a real candidate freeze or pre-exposure success.

Independent reviewer-medium found no material findings and independently passed
all eight scratch tests (review.json). The production domain/runtime checks are
delegated to the existing runner and remain unexecuted against the absent final
manifest. freeze-1818.txt records the unchanged frozen macOS26.5 evidence check.
