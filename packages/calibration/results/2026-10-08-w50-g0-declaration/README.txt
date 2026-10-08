W50 G0 declaration tools

No root hashes are supplied by assembly. On the assembled, reviewed tree only:

  python3 -I references.py --check
  python3 -I assemble.py
  python3 -I declare.py hash
  python3 -I declare.py check --phase native

Run from any working directory; paths are anchored to these files. Assembly refuses existing
root seals. The native contract and its sidecar must exist and be source-pinned before hashing.
No hash/amend/reselection path exists after the root seal.

The native driver calls declare.verify(phase='native') in-process, then verifies its own fixed
batch contract and enforces that contract's transitive import closure before planning/launch.
A positive Screen Recording grant, instrument admission and census are separate requirements;
a valid declaration is not a grant or a successful capture.

The audit/next_wave.py, closure.py and renderer_template.py files are prospective copies of
W49b's required templates. audit/render.py is the canonical compare entrypoint with that binding
inside it. Its fixed contract is audit/execution-contract.json. audit/probe.py dry-exercises its
planner and membership checks; tests construct temporary contracts, never a live experiment seal.
The renderer exposes no alternate scene, candidate, domain or contract arguments. Execution is
scratch-only, writes the actual command and material provenance, and checks exact capture rows.
Before any helper executes, a stdlib-only bootstrap verifies source bytes, then installs the
source-only import guard. Candidate phases are gate and exposure only; each requires the pre-fit
seal to authorise the exact web contract and sidecar. A self-seal alone grants nothing.
Current-material strict reads are NOT a candidate phase: their gate0 response is the defect being
measured, not a live-chart candidate that can pass the new numerical referee. Those pre-fit reads
and the custom 512x384 new-bed compare/measurement adapter need a separately declared G1 instrument.
They are explicit pre-fit blockers, not a numerical-safety bypass or a native operational blocker.
Every execution run also requires a pinned, candidate-bound numericalReferee report covering the
full composed low-end domain, fixed join, existing eligibility stand-downs and structured sample
arguments, with no negative pre-clamp neutral request. audit/numerical.ts produces these reports;
missing measured inputs block rather than yield a synthetic PASS. audit/numerical_guard.py checks
explicit cohort, candidate/endpoint, argument/evidence and fixed-reference pins independently. Its
reported runtimeSources must exactly match the assembled Node-load witness audit/runtime-closure.json,
and sources must equal that complete runtime/input union. Correct-looking numbers with one arbitrary
unchanged source pin cannot authorise a render. Synthetic runtime tests are not fitted admissibility.
An exposure additionally binds the frozen candidate and complete exposed gate report, and claims
exposure-started.json exclusively before launching. Failed or interrupted exposures cannot retry.

references.json is the pre-native identity inventory, not a readiness report. Known dark0.25
T1 values and historical caps come from committed W49a/W49b evidence. The missing active0.5
ml/lg current captures at both scales now bind named G0 scratch controls on both tiers. Their
path-cut readings and bars remain unmeasured; no baseline or statistic advances from adding capture
provenance. Two missing default2x receded CSS impulse ml/lg references complete the original two-tier
low-end price, with its fixed <=1-code error-growth budget and unknown path statistics. No fine-checker
row is added merely because it was captured. Each unknown says UNMEASURED. The four pre-change dark
source documents are preserved by full hash under references/documents/. Historical generations and capture-tree
owners remain unchanged.

Before fitting, pre-fit-evidence.json plus its immutable .sha256 must bind a completed reference
file and each required proof listed in fit-declaration.json. This is an additive evidence seal,
not permission to edit either operational part. declare.verify(phase='fit') checks the root
parts, exact reference membership, fixed roles/support/document pairs/historical caps and all
already-known values/hashes before accepting new evidence. Every exposed reference must be
MEASURED. Blind references must be SEALED_BLIND, carry only identity/dependency provenance and
must not contain native/current/fidelity/B statistics. Do not open them to complete this phase.

A pre-fit proof has schema w50-prefit-proof-1, its required kind, status PASS, nonempty uniquely
named checks each with status PASS, and nonempty source/output pin lists. Empty files, a bare
PASS flag or a missing adapter/reference/closure proof are not acceptable evidence. Pin paths
are repository-relative; source/output bytes must exist and match. Reference capture paths can
be absolute to the capture machine and are separately hash-checked. The required proofs include
the actual new-bed renderer adapter and its exercised measurement/band closure. No completed
pre-fit seal or successful fitting proof is supplied at G0.

Checks (no native/web capture):
  python3 -I test_declare.py
  python3 -I test_references.py
  /Users/new/vitrea-w49/py/bin/python -I audit/test_execution.py
  python3 -I audit/test_membership.py
  python3 -I audit/test_numerical_guard.py
  /Users/new/vitrea-w49/py/bin/python -I audit/probe.py
