#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Owner self-check: the prepared CURRENT owner report graded as the candidate (DL5m 1, 5).

The owner counterpart of DL5m item 6's target witness. The judge config's ownerUnion pins the
prepared current report; that report is graded here through the judge's own
grade_owner_report, at the config's membership, against the config's owner contracts and the
original inventory's 640 owner keys. Current read as the candidate must leave nothing to
excuse: every owner-contract cell, every context cell and every aggregate PASS. A cell or
aggregate the current material cannot pass would make the one exposure unpassable whatever
the candidate draws, which is what the eight dark inactive dark-solid cells did before
7e621f344.

X75 and X76 are candidate-only intrinsic checks; the prepared report carries them UNMEASURED
by construction (no candidate documents exist), so they are counted and not graded here.

  owner_selfcheck.py [CONFIG] [--write PATH]

CONFIG defaults to judge/config.json. Stdout and the optional write-once witness carry pins,
statuses, counts and cell identities only, never a reading (DL5k). Exit 0 only on PASS.
"""
import collections
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
SCHEMA = 'w50-owner-selfcheck-1'


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


J = source(HERE/'live.py', 'w50_owner_selfcheck_judge')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(REPO))


def checked(pin):
    path = Path(pin['path'])
    path = path if path.is_absolute() else REPO/path
    if not path.is_file() or sha(path) != pin['sha256']:
        raise ValueError('Changed or missing pinned input: '+pin['path'])
    return path


def owner_keys(inventory):
    keys = [[c[k] for k in J.KEY] for c in inventory['cells'] if c['statistic'] == 'owner-contracts']
    if len(keys) != 640 or len({tuple(k) for k in keys}) != 640:
        raise ValueError('The original inventory must carry exactly 640 owner keys')
    return keys


def membership_of(report):
    """The membership a judge config pins for this report: its own sorted keys."""
    return {'cells': sorted(report['cells']), 'aggregates': sorted(report['aggregates'])}


def grade(report, contracts, keys, membership):
    """Grade a prepared report as the candidate; counts and failing identities only."""
    graded = J.grade_owner_report(report, keys, contracts, membership)
    owners = {'/'.join(k[:3]) for k in keys}
    count = lambda items: dict(sorted(collections.Counter(i['status'] for i in items).items()))
    cells = [dict(g, id=i) for i, g in graded['cells'].items()]
    owner_cells = [c for c in cells if c['id'] in owners]
    failing = sorted(c['id'] for c in cells if c['status'] != 'PASS')
    status = 'PASS' if not failing and all(a['status'] == 'PASS' for a in graded['aggregates']) else 'FAIL'
    return {'status': status,
            'counts': {'cells': len(cells), 'ownerCells': len(owner_cells),
                       'contextCells': len(graded['context']), 'aggregates': len(graded['aggregates'])},
            'statuses': {'ownerCells': count(owner_cells), 'contextCells': count(graded['context']),
                         'aggregates': count(graded['aggregates'])},
            'aggregates': graded['aggregates'],
            'notPassing': [{'id': i, 'axes': sorted(a for a, v in graded['cells'][i]['axes'].items()
                                                    if v['status'] != 'PASS')} for i in failing],
            'intrinsicNotGraded': count(graded['intrinsic'])}


def selfcheck(config_path):
    config = J.parse(Path(config_path).read_bytes())
    union = J.owner_membership(config['ownerUnion'])
    report = J.parse(checked(union['report']).read_bytes())
    contracts = J.parse(checked(config['ownerContracts']).read_bytes())
    inventory = J.parse(checked(config['references']).read_bytes())
    if membership_of(report) != {'cells': union['cells'], 'aggregates': union['aggregates']}:
        raise ValueError('Judge config ownerUnion differs from its prepared report\'s membership')
    result = grade(report, contracts, owner_keys(inventory), union)
    return {'schema': SCHEMA, **result,
            'config': {'path': rel(config_path), 'sha256': sha(config_path)},
            'preparedReport': union['report'], 'ownerContracts': config['ownerContracts'],
            'inventory': config['references'], 'grader': {'path': rel(HERE/'live.py'), 'sha256': sha(HERE/'live.py'),
                                                          'function': 'grade_owner_report'}}


def main(argv):
    write = None
    if '--write' in argv:
        index = argv.index('--write'); write = Path(argv[index+1]); argv = argv[:index]+argv[index+2:]
    config = Path(argv[0]).resolve() if argv else HERE/'config.json'
    result = selfcheck(config)
    raw = (json.dumps(result, indent=1, allow_nan=False)+'\n').encode()
    if write is not None:
        with write.open('xb') as handle: handle.write(raw)
    sys.stdout.write(raw.decode())
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
