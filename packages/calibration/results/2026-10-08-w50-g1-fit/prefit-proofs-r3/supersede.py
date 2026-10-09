#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Record, once, which pre-fit proofs the r3 rebuild superseded (DL5o, in DL5l's pattern).

The LIVE lineage check (live-execution/authority.py supersession_records, series
prefit-proofs-r{n}/supersedes.json) refuses any pin of a file a record names under `superseded`.
After build.py has rebuilt the four kinds whose pins moved with the r3 owner chain, this writes
prefit-proofs-r3/supersedes.json naming the r2 proofs they replace and the r3 proofs that replace
them. The six proofs in prefit-proofs/ stand and are named as standing. Pins only.

  supersede.py
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
REBUILT = ('active05ScratchBaselines', 'dark05Bands', 'referenceCompletion', 'repeatBar')
STANDING = ('identityDigestsGoldens', 'nativeArchive', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
            'numericalRehearsal', 'shaderCpuAgreement')


def pin(path):
    path = Path(path).resolve()
    return {'path': str(path.relative_to(REPO)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    record = {
        'schema': 'w50-prefit-proof-supersession-1',
        'ruling': 'DL5o (a), recovered in DL5l\'s pattern; DL5m item 5 (X75/X76 records at both positions)',
        'cause': 'the r3 owner chain (owner/r3/supersedes.json, completion/registered-3/supersedes.json) moved the '
                 'completed reference inventory and its assembly, which these four proofs pin',
        'superseded': {'proofs': {kind: pin(FIT/'prefit-proofs-r2'/f'{kind}.json') for kind in REBUILT},
                       'status': 'retained unedited; each validated against the r2 inventory it pins'},
        'rebuilt': {kind: pin(HERE/f'{kind}.json') for kind in REBUILT},
        'standing': {kind: pin(FIT/'prefit-proofs'/f'{kind}.json') for kind in STANDING},
        'builder': pin(HERE/'build.py'),
    }
    with (HERE/'supersedes.json').open('xb') as handle:
        handle.write((json.dumps(record, indent=2, allow_nan=False)+'\n').encode())
    print(json.dumps(pin(HERE/'supersedes.json')))


if __name__ == '__main__':
    main()
