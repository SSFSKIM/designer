#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Build the hypothetical identity candidate the owner self-check grades X76 on (DL5o).

DL5o: before the successor LIVE root seals, the owner self-check grades X76 at both positions on
a hypothetical identity candidate, the current documents plus the required records. This makes
that candidate once, write-once, under owner/r3/identity/:

  glass025/, glass05/   fit/candidate.ts buildCandidate(baseline, null, ...) over the current-
                        material declarations inputs/current-material/glass{025,05}/candidate.json
                        (the current documents, profileKey only differing): dark patches and
                        digests unchanged, the DL5o holds added to the receded dark entries;
  records/              live-run/batches.py owner_intrinsic_records over that cohort, so the
                        envelopes are derived exactly as the live gate and exposure batches derive
                        them, against the G0 references' before pairs.

  identity.py build
Stdout carries pins only.
"""
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parents[1]
REPO = FIT.parents[3]
CAL = REPO/'packages/calibration'
OUT = HERE/'identity'
BASELINES = {'glass025': FIT/'inputs/current-material/glass025/candidate.json',
             'glass05': FIT/'inputs/current-material/glass05/candidate.json'}
REFERENCES = {'path': 'packages/calibration/results/2026-10-08-w50-g0-declaration/references.json',
              'sha256': 'a666c1b00f4b1aff48bddeca9dacc1c1bc05dcf83bf908efddbe46c24c322d0c'}


def module(path, name):
    loaded = types.ModuleType(name); loaded.__file__ = str(path); sys.modules[name] = loaded
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), loaded.__dict__)
    return loaded


def build():
    B = module(FIT/'live-run/batches.py', 'w50_identity_batches')
    if OUT.exists(): raise ValueError('The identity candidate is write-once')
    OUT.mkdir()
    cohort = []
    for name, baseline in BASELINES.items():
        pin = B.D.pin(REPO, baseline)
        result = subprocess.run(['node', '--import', 'tsx', str(HERE/'identity-build.ts'), str(REPO/pin['path']),
                                 pin['sha256'], str(OUT/name)], cwd=CAL, capture_output=True, text=True, check=True)
        built = json.loads(result.stdout)
        cohort.append(B.D.pin(REPO, Path(built['path'])))
    records = B.owner_intrinsic_records(REPO, REFERENCES, cohort, OUT/'records')
    print(json.dumps({'cohort': cohort, 'records': records}, indent=1))


if __name__ == '__main__':
    if sys.argv[1:] != ['build']: raise SystemExit(__doc__)
    build()
