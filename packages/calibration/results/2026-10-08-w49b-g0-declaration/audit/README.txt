Additive W49b post-seal audit and prospective execution template

Authority
---------
This directory supplements, and does not amend, fb74ebc1e54cdb5c668df64d04f9d717fdfc3770.
Part 1 remains f8cf52f6846977e32afa322b1890aa7180acd2ca1d39f1bbe2bf584d59311b2e;
part 2 remains 0bbad26c0fd1bec4b196424c4a04e53faeb81e04f38c37eb358a1ce7c097a715.
The registered identification batch is read from that seal, not defined by a caller's inputs.
There is no new rung, fit domain, metric, selection rule, root seal, reading or verdict here.

Final actual-record audit (after the registered job finishes)
---------------------------------------------------------
A=/Users/new/vitrea-w49/b-g0/packages/calibration/results/2026-10-08-w49b-g0-declaration/audit
P=/Users/new/vitrea-w49/py/bin/python
"$P" -I -B "$A/audit.py" \
  --candidates /Users/new/vitrea-w49/b-g0-scratch/candidates \
  --renders /Users/new/vitrea-w49/b-g0-scratch/renders \
  --out "$A/actual-record.json"

Commit the actual PASS/FAIL record before the ladder's charter verdict. The output file is
exclusive-create: a rerun needs a new filename and retains the earlier record. Exit 0 means
provenance/membership PASS, not PASS-to-fit. Exit 1 means FAIL, including an unfinished final
job. --partial yields an INCOMPLETE diagnostic (exit 2), never PASS, even if all data exists.
Invalid evidence still fails. Do not use a partial diagnostic as the final actual-record audit.
A running job can change between the opening and closing checks; that fails closed and is
not permission to overwrite its evidence. Run the final audit on the completed, stable job.

What is checked
---------------
* Both sealed declarations, all their source pins, reference/snapshot/generation pins, and
  the actual root plan against the registered 27 points, 54 runs and 1,686 gate cells.
* Every candidate point and build record against the sealed point. All four endpoint
  documents are reconstructed semantically from pinned snapshots plus that point's patches.
  The driver's real CPU reader independently checks their resolved digests and X75.
* Exact requested/planned/measured membership, launch argv, completed matrices, census/browser
  pins, lock witnesses, completion hashes and physical capture membership. Extra/withheld
  scenes are rejected by names before opening their captures. Capture reports also identify
  the endpoint and sampling backend that actually drew, rather than only the requested one.
* Original completed PNG/metadata byte witnesses. The driver's additional alpha/report files
  receive additive witnesses, explicitly separate from the original completion witnesses.
* Only measured GATE native fixtures and backgrounds are hashed against git bytes at the seal
  commit. No withheld fixture/capture bytes are opened. No PNG is decoded by the audit.
* The Python measurement closure is discovered under the pinned arm64 interpreter with -I,
  by executing a synthetic dry instrument exercise and tracing imports, exec and function
  sources. Repository source is compared with git bytes at the seal before execution; stale
  repository .pyc files are not used. Geometry and luminance live in the discovered interior
  port, not an assumed separate module. Python/NumPy/SciPy/Pillow, Node/pnpm/Playwright versions
  are recorded. The opening and closing evidence/source checks must agree.

This proves the CURRENT source/evidence bytes against the seal commit. It is not a historical
process attestation that an earlier reader used this wrapper, interpreter or import gate.
The synthetic probe discovers exercised dependencies; it opens no real pixels and chooses
no ladder verdict. No GPU process, browser, native harness, fitting or publication is launched.

Future uses of the frozen G0 launcher
------------------------------------
"$P" -I -B "$A/guard.py" --candidates /Users/new/vitrea-w49/b-g0-scratch/candidates

This validates and prints PRELAUNCH_BOUND, plan-only. For a separately authorised future
execution, add --out <new scratch directory> --execute. It passes only the registered sealed
batch to the unchanged render.py. An optional --batch is admitted only at identical bytes.
There is no --labels or arbitrary-batch execution pathway in the wrapper. It cannot retrofit
provenance to the job already launched. The final audit remains necessary.

Next-wave prospective template (not applied to frozen W49b tools)
----------------------------------------------------------------
Copy next_wave.py, closure.py and renderer_template.py together into the next wave's tools.
Use a dry probe that imports the renderer and exercises the actual planner/measurement
routes without reading withheld pixels or starting a render. The executable renderer example
is CPU plan-only; its fixed execution-contract.json path and pre-planning binding are the
parts to retain when replacing its final output block with that wave's authorised launcher.

Run the COPIED next_wave.py before any new reading:
  <pinned-python> -I -B <copied-next_wave.py> seal \
    --root <next-checkout> --batch <registered-batch.json> \
    --probe <dry-probe.py> --renderer <copied-renderer_template.py> \
    --contract <tools>/execution-contract.json

The NEXT ROOT declaration must pin execution-contract.json AND its .sha256, together with
these guard/template files. Do not treat a caller-selected contract as root authority. Seal
refuses existing output/sidecar; it has no amendment or rehash verb. Verification re-executes
the probe and requires identical source closure, probe bytes and environment. The actual
renderer itself verifies its fixed contract and batch before planning, even if the outer
wrapper is bypassed, and installs an import gate for the real process. A later repository
import absent from the dry closure, or changed from it, fails BEFORE that module executes.
Add the same gate to a separately spawned measurement-reader process; a parent's Python hook
does not propagate across a process boundary. Declare that reader's entrypoint/dry exercise
in the prospective closure too. A newly needed dependency requires a new prospective wave,
not editing an existing seal after readings.

The next_wave.py render command is a convenience for a contract-bound renderer:
  <pinned-python> -I -B <copied-next_wave.py> render \
    --root <next-checkout> --batch <registered-batch.json> \
    --contract <tools>/execution-contract.json -- <renderer-options>
It always passes the registered batch as the renderer's first positional argument.

Tests
-----
"$P" -I -B "$A/test_audit.py" -v

The evidence tests copy only the completed identity point's two runs (132 cells) and the
actual candidate build. They keep the full sealed root plan; that subset can never pass a
whole-run final audit. Mutations test off-domain batch substitution, changed instruments,
missing/extra cells and runs, altered candidates/points/captures, withheld requests, actual
launch-argv changes, direct renderer binding, and unsealed imports at real execution time.
Tests write only temporary fixtures and this directory's new source files; no render or
existing evidence is changed.
