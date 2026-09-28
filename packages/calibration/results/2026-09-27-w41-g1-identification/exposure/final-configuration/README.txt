W41 G1 — final exposure configuration (BODY-E3 only), prepared for review and freeze
=================================================================================

This directory prepares the complete static input to the ONE production freeze under
claims §5.192 and charter clauses 2/11. It is not a freeze, preflight, browser run,
native read or receipt, and it changes no runner, runtime, scorer or earlier evidence.

What will be frozen
-------------------
configuration.json is the binding data. It names, each with its SHA-256:

  candidates   [body-e3]  exposure/assembly/body-e3-2/candidate.json
                          (light-inactive E3; parameters/predictions from candidate-e3/public-2,
                          rendered/identity/survival from body-e3-2, the body-e3 claim scope,
                          candidate-capture/attempt-1/domain-evidence.json)
  config       candidate-capture/attempt-1/runtime.json  (four profiles' material/receded
                          documents, the generated-backdrop bundle, two policy snapshots)
  scorer       candidate-e3/scorer.py                      (4d7a1def…, reviewed; not imported here)
  declaration  2026-09-27-w41-g0-declaration/bounds-declaration.txt  (unchanged G0)
  closure      2026-09-27-w41-g0-declaration/closure.json            (unchanged G0)
  instruments  final-configuration/instruments.json        (complete sorted list)
  manifest     final-configuration/manifest-1.json         (output; must not exist yet)

runner.py is 5ae591ad (the reviewed cumulative X6 guard); historical 02ed4421 pins are
carried by transition/bridge.py and reading-1.json, both in the list. No executable
change is part of this configuration.

instruments.json = the E3 assembly's 5,780-entry list, unchanged, plus the additions
listed by group and reason in configuration.json's instrumentComposition, plus these
two configuration files themselves. The groups: the runner/X6/X6-wait review chain;
the assembly and its review/index; the source transition; BOTH readiness records
(00071284, beeb896b) with their indexes and the ownership/origin supplements
(28675423, 812bf106), not re-audited; the preflight; the X6 observer evidence; the
E3 numerical and rendered-capture review chains; the scratch leaf, integration and
close checks; body and spatial dispositions; G1 top-level rulings; the G0 declaration
record; stroke certified exclusions; M1 light-inactive transfer (fdae0526) and its
reviewed verdict (33718e2e); the M2 disposition chain with its one completed start,
its terminal record (afed9dc3) and the six partial records that record rests on
(static-partitions-1 A/B stdout, execution, calibration admission), pinned once the
host restart had ended both writers. Deliberately NOT pinned: the
spec and claims ledgers and the G1 top-level README (living documents; runner.verify
refuses a pinned file that moves before the receipt), this README, the checker and
its transcripts, css-projection/ (Decision Log 4, G2), and stroke fitting machinery.

Freeze also adds, by itself, every automatic source (runner.sources(): runtime source
roots plus every *.py under the four instrument roots; 418 files since 33718e2e added
verdict2_witness_replay.py) and the candidate's own files; see static-check-2.txt for
the prospective pinned-file count (6,575).

Dispositions
------------
Body: E3 light-inactive, the only candidate. Spatial: a finding, no leaf (DL6).
Stroke: held-shadow, M0, M1 dark-inactive and CSS width certified rejected; M1
light-inactive has no survivor (local fitted failure, all 16 strata, 33718e2e); M2
UNMEASURED, unfinished and not rejected (c76f949d, restoring the relayed user ruling);
its terminal record (stroke/M2-terminal-record-1.json, afed9dc3) records device starts
1 and 2 ABORTED_UNSCORED by the 2026-09-28T22:24:32Z host restart and no further start.
No disposition is pending.

Static check
------------
static-check.py.txt mirrors runner.freeze's production branch with the runner's own
read-only helpers and never calls freeze, verify, a Receipt or the scorer. It is .txt
so that it does not join the frozen source inventory. From the worktree root:

  PYTHONDONTWRITEBYTECODE=1 python3.12 -B - < \
    packages/calibration/results/2026-09-27-w41-g1-identification/exposure/final-configuration/static-check.py.txt

Exit 0 READY, 2 PENDING (a placeholder only), 1 FAIL. static-check-1.txt (11caaa2c,
PENDING on the M2 record) and static-check-2.txt (afed9dc3, READY, 6,411 instruments)
are its records, each naming the HEAD it read. It predicts freeze's refusals; it does
not substitute for them.

Remaining order (steps 1-2 done; nothing after them has been done)
-------------------------------------------------------------------
1. DONE: the M2 terminal record is supplied and pinned with its six partial records;
   instruments.json regenerated (6,411); static-check-2.txt exits 0.
2. DONE: final independent review (reviewer-high, review-1.json): no material findings.
   Committed with this directory.
3. Source quiescence from here until the receipt ends: no edit to any pinned file and
   no new *.py under the four instrument roots or the runtime source roots (an added
   Python file changes runner.sources() and verify refuses). Any change means a new
   configuration and manifest-2, never a repointed manifest-1.
4. Static freeze, the recorded command (no new entrypoint: runner.freeze suffices, and
   a new .py would itself enter the source inventory). The static freeze does not
   require the hands-off confirmation:

----8<---- (copy verbatim, unindented) ----
cd /Users/new/vitrea-w41/g1
F=packages/calibration/results/2026-09-27-w41-g1-identification/exposure/final-configuration
set -o noclobber
PYTHONDONTWRITEBYTECODE=1 python3.12 -B - > "$F/freeze-1.txt" 2>&1 <<'EOF'
import hashlib, importlib.util, json, os, sys
from pathlib import Path
sys.dont_write_bytecode = True
G1 = 'packages/calibration/results/2026-09-27-w41-g1-identification'
F = G1 + '/exposure/final-configuration'
spec = importlib.util.spec_from_file_location('w41_final_freeze_runner', G1 + '/exposure/runner.py')
runner = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)
root = runner.ROOT
assert root == Path('.').resolve()
cfg = runner.load(root / F / 'configuration.json')
runner.committed(root, F + '/configuration.json'); runner.committed(root, F + '/instruments.json')
assert all(item['path'] for item in cfg['pendingDispositions']), 'disposition still pending'
refs = [cfg[k] for k in ('runner', 'boundary', 'config', 'scorer', 'declaration', 'closure')]
for ref in refs + cfg['candidates'] + cfg['pendingDispositions']:
    assert runner.committed(root, ref['path']) == ref['sha256'], ref['path']
instruments = runner.load(root / cfg['instruments']['path'])
assert len(instruments) == cfg['instruments']['count']
manifest = runner.freeze(root, runner.boundary.default_wave(),
                         [runner.load(root / c['path']) for c in cfg['candidates']],
                         config=cfg['config']['path'], scorer=cfg['scorer']['path'],
                         declaration=cfg['declaration']['path'], closure=cfg['closure']['path'],
                         instruments=instruments)
out = root / cfg['manifest']
with out.open('x') as stream:
    json.dump(manifest, stream, indent=1, sort_keys=True, allow_nan=False)
    stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
print(cfg['manifest'], hashlib.sha256(out.read_bytes()).hexdigest(),
      manifest['revision'], len(manifest['files']), len(manifest['sourceFiles']))
EOF
----8<----

   Commit manifest-1.json with freeze-1.txt in the next commit. A refusal leaves no
   manifest; record it and repair the input, never loosen the runner.
5. External preflight (preflight/README.txt) with
   FINAL_COMMITTED_MANIFEST=$F/manifest-1.json and a new evidence path, run immediately
   before the receipt; recheck the browser path, Info.plist version, executable and
   framework hashes against readiness-2026-09-29/browser-attestation.json, and the
   recursive manifest, without launching it. No install, download, cache or config
   change; restoring the backup needs explicit recovery authorization.
6. Only after explicit hands-off-window confirmation, with fresh X6 gates:
     runner.run_production(<absolute committed manifest-1.json>,
                           <new absolute output directory outside the repository>)
   One begun attempt; no retry on capture, equality or scoring failure.

Environment facts carried forward: full Chromium 1234 / 151.0.7922.34 matches all 600
candidate descriptors; historical binary-byte identity is UNPROVEN and the in-receipt
PNG/projection equality is the binding check. Python 3.12, NumPy 2.3.5, Pillow 12.3.0
match candidate-e3/runtime.json. The backup at /Users/new/vitrea-w41/browser-backup/
chromium-1234 was verified by both readiness records and was not re-audited here.
