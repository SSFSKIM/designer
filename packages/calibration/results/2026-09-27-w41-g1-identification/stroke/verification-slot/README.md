# Completed-start resource-only verification

One invocation runs one mode in its own process. The parent first freezes/reviews
these sources and authors an external admission receipt; the adapter does not
create authority, stop processes, transfer candidate ownership, schedule work,
retry failures, or compare/adopt the two results. It never creates a candidate
claim or writes candidate results. The production CLI alone imports and invokes
memoization/proof.py native_once(mode, out, admit).

```sh
python verification_slot.py --root /absolute/scheduler-root \
  --receipt /absolute/parent-receipt.json --sha256 <receipt-sha256>
```

The parent receipt is JSON with these fields:

```text
  kind: "STROKE_VERIFICATION_ADMIT"
  schedulerRoot: canonical absolute existing scheduler root
  heldRevision: "d35b4cbf43f1fcdda55063b3b8e0fa178d720a78"
  roster: {path, sha256}, identical to this root's registered roster reference
  captureRelease: {path, sha256}, existing CAPTURESRELEASE for this root
  peakEvidence: {path, sha256}, existing STROKE_PEAK_RSS evidence
  reservationBytes, oldWorkerReservationBytes, maxConcurrency:
    the existing scheduler admission fields, with its unmodified rules
  mode: "unwrapped" or "wrapped"
  out: canonical, new absolute directory beneath stroke/memoization/
  completedArtifact: {path, sha256}, exactly the existing
    stroke/survivor-scope-partition-0/device-M1-start-00.json
  sourceSha256: absolute-path-to-SHA256 mapping, containing every path returned
    by verification_slot.required_sources(); additional pins are also checked
  predecessor: null for unwrapped; for wrapped a {path, sha256} reference to
    this root's verification/unwrapped/terminal.json

```

All referenced files must exist at their pinned bytes. Wrapped additionally
normally requires a verified unwrapped terminal, unchanged referenced lease/admission,
identical source pins, completed artifact and roster, and the persisted proof's
full artifact set at its declared hashes. A proof from another root, a failed
proof without the narrowly scoped recovery below, or a bare unwrapped result is not a predecessor.

## Saved-comparison recovery predecessor

A wrapped admission may additionally contain `comparisonRecovery` with two
hash-pinned references, `direction` and `proof`. The ordinary `predecessor` still
names the **original failed unwrapped terminal**, never a fabricated successful
view. The parent-authored direction must have these fields:

```text
kind: "STROKE_VERIFICATION_COMPARISON_RECOVERY"
schedulerRoot: the same canonical root
failedTerminal: the exact predecessor {path, sha256}
recoveredProof: the exact comparisonRecovery.proof {path, sha256}
sourceTransitions: {
  absolute-source-path: {oldSha256: old-execution-hash, newSha256: current-hash}
}
```

This route admits only a terminal with `failed-after-solver-start`, both admission
stages, `solverStarted: true`, and the retained `AssertionError` for the completed
native raw result's exact typed/bit comparison. The terminal, original lease and
admission must agree on root, mode, PID, held revision, roster and completed
artifact. Generic solver failures and unstarted work are not recoverable here.

The separate proof is the helper's `w41-memoization-native-one-mode-1` saved-comparison
receipt. Its `artifactDirectory` must be the old admission's output; all three saved
artifact hashes are checked there. Its `comparisonRerun` must report zero optimizer
runs and native archive reads, cite the exact failed terminal, and identify the
current comparator plus its hash-pinned driver compatibility amendment and diff.
The recovered proof must retain the saved replay's original execution sources,
typed live-result witness, trace and environment; its JSON-boundary witness is
separate. Numerical/trace re-verification belongs to the reviewed helper, not a
second comparator implementation in this resource adapter.

Source membership cannot change. The direction's transitions must enumerate
**exactly** the changed hashes, restricted to `memoization/proof.py` and this
`verification_slot.py` validator. The comparator's old/new pair must also match
its compatibility amendment. Every fitting, wrapper, fixture, partition,
scheduler and other source remains identical. This is not authority for a memory
policy or driver change; such work needs its own admission design.

No terminal, lease, old source map or saved solve is rewritten. The comparison
recovery itself does not launch a proof; only a separately admitted wrapped CLI
invocation can proceed. A recovery field is refused on an unwrapped invocation.

The allocation flock is held from receipt validation through the proof and
terminal publication. Both verification modes and scheduler claims/handovers use
that SAME lock. Existing old static fits continue; scheduler admission counts
the live roster and existing claims, observes their RSS, enforces its concurrency
cap, pressure policy, monotonic peak reservation and 3 GiB headroom floor.
Before preparation the new verification's whole peak is reserved. Immediately
before fitting its already-resident RSS is included by the scheduler's own
admission routine. No second memory-policy implementation exists here.

The admission API calls its resident-owner argument `own_claim`. To avoid inventing
one, the adapter uses `importlib.util` to load scheduler.py as a private module
object named `s` (spec name `verification_scheduler`), then wraps exactly the module
attribute **`s.claim_name`**, retaining its original function as `_candidate_name`.
The wrapper extends naming only for an adapter `VerificationOwner` object. This object has no candidate task
or generation; its verification-<mode> label cannot equal a real candidate file.
Every ordinary claim is named by the original unchanged function. The memory
routine itself is unchanged, including its old-worker and candidate enumeration.
Before-preparation admission logs identify M1/device/start0 as the verification
SUBJECT; that log context grants no candidate ownership. This process-local naming
bridge changes neither scheduler source bytes nor other running scheduler modules.

Operational limitation: a parent may stop an old worker externally, but an
ownership transfer/new scheduler admission waits for the verification lock.
This is not a responsive queue. There is no automatic launch of wrapped when
unwrapped finishes: a fresh external receipt and a second CLI process are needed.

Evidence under `scheduler-root/verification/<mode>/` is immutable:

```text
  lease.json: actual PID, mode, external receipt and held allocation lock
  before-preparation-admission.json, before-fit-admission.json: admitted gates
  solver-verification-start.json: durable marker before native_once can enter
    its first optimizer; a boundary marker, not evidence of fit completion
  terminal.json: verified with a hash-pinned completed-start-proof.json, or an
    explicit failed/refused/no-fit outcome without a success proof reference

```

The caught-end terminal reports the actual process ru_maxrss on Darwin, explicitly
in bytes. A matching resource-only rss-verification-<mode>.json in admissions/
is compatible with Store.observed_rss(), so later admissions retain that peak
on refusal, preparation failure and solver failure as well as success. Arrays
prepared without a successful before-fit gate are never called a solver run.

There is one immutable slot per mode per root, including failed/refused attempts.
A crash/kill may leave a lease or solver-start marker without a terminal or final
peak. It is not a free slot; the parent must reconcile it. There are no automatic
retries, record overwrites, lease cleanup or recovery commands. The tool cannot
prevent unrelated code that ignores the allocation lock from starting work.

Synthetic checks (no native archive, real optimizer or process controls):

```sh
python -m unittest discover -s /absolute/stroke/verification-slot -p 'test_*.py'
```

## Current state: W41 G1 PID-reuse fix

The paragraphs above are kept as written for their epoch. Two statements in them
are no longer literally true. First, scheduler.py's bytes changed: the live-owner
and candidate enumeration moved into one v1 routine, `Store.reservations`, which
every gate calls. An old owner with a registered handoff never reserves, and a
candidate claim reserves only while its recorded claimant identity (PID, start
time, full command) holds its PID. So the "counts the live roster and existing
claims" admission above counts live owners by identity, and a new verification
receipt's `sourceSha256` must pin the new scheduler.py. Second, the own-claim skip
now runs inside that v1 routine through the private module's `s.claim_name`, so
the `VerificationOwner` naming bridge still applies unchanged: it cannot skip a real
candidate claim. The verification lease is still not a candidate claim; the
claimant lifecycle checks never apply to it, and admissions add `excludedProcesses`.
