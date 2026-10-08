#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Owner self-check: the prepared CURRENT owner report graded as the candidate (DL5m 1, 5; DL5o).

The owner counterpart of DL5m item 6's target witness. The judge config's ownerUnion pins the
prepared current report; that report is graded here through the judge's own
grade_owner_report, at the config's membership, against the config's owner contracts and the
original inventory's 640 owner keys. Current read as the candidate must leave nothing to
excuse: every owner-contract cell, every context cell and every aggregate PASS. A cell or
aggregate the current material cannot pass would make the one exposure unpassable whatever
the candidate draws, which is what the eight dark inactive dark-solid cells did before
7e621f344.

X75 and X76 are candidate-only intrinsic checks: the prepared report carries them UNMEASURED by
construction. Until DL5o they were counted and not graded, which is how X76 could never read
MEASURED at glass 0.5 without anything failing. Now they are GRADED (DL5o): the frozen owner
engine the live owner runs (owner-candidate/bridge.ts selfcheckIntrinsics, through the live
owner config's registered frozen closure and source pins) reads X75 and X76 on the hypothetical
identity candidate of owner/r3/identity (the current documents plus the records DL5o requires,
built by owner/r3/identity.py), and that intrinsic report replaces the prepared report's
placeholder before grade_owner_report grades everything. PASS needs X75's twelve endpoints and
X76 at 0.25 and 0.5 within, as DL5m 5 requires of the exposure.

  owner_selfcheck.py [CONFIG] [--owner-config PATH] [--records PATH] [--write PATH]

CONFIG defaults to judge/config.json, the owner config to live-roles/owner-config.json and the
records to owner/r3/identity/records/owner-intrinsic-records.json. Stdout and the optional
write-once witness carry pins, statuses, counts, leaf and family names and cell identities only,
never a reading (DL5k). Exit 0 only on PASS.
"""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = HERE.parents[4]
CAL = REPO/'packages/calibration'
SCHEMA = 'w50-owner-selfcheck-2'
OWNER_CONFIG = FIT/'live-roles/owner-config.json'
IDENTITY = FIT/'owner/r3/identity/records/owner-intrinsic-records.json'
RUNNER = HERE/'owner-selfcheck-intrinsic.ts'
BRIDGE = FIT/'owner-candidate/bridge.ts'


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


J = source(HERE/'live.py', 'w50_owner_selfcheck_judge')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(REPO))
def pin(path):
    path = Path(path).resolve()
    return {'path': rel(path) if path.is_relative_to(REPO) else str(path), 'sha256': sha(path)}


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


def grade(report, contracts, keys, membership, intrinsic=None):
    """Grade a prepared report as the candidate; counts and failing identities only.

    Without `intrinsic` the report's own placeholder is counted, not graded (the pre-DL5o
    reading, kept for the recorded r2 witness). With it, the intrinsic report replaces the
    placeholder and every X75/X76 member must PASS too."""
    graded = J.grade_owner_report(report if intrinsic is None else dict(report, intrinsic=intrinsic),
                                  keys, contracts, membership)
    owners = {'/'.join(k[:3]) for k in keys}
    count = lambda items: dict(sorted(collections.Counter(i['status'] for i in items).items()))
    cells = [dict(g, id=i) for i, g in graded['cells'].items()]
    owner_cells = [c for c in cells if c['id'] in owners]
    failing = sorted(c['id'] for c in cells if c['status'] != 'PASS')
    passing = not failing and all(a['status'] == 'PASS' for a in graded['aggregates'])
    if intrinsic is not None:
        passing = passing and all(i['status'] == 'PASS' for i in graded['intrinsic'])
    result = {'status': 'PASS' if passing else 'FAIL',
              'counts': {'cells': len(cells), 'ownerCells': len(owner_cells),
                         'contextCells': len(graded['context']), 'aggregates': len(graded['aggregates'])},
              'statuses': {'ownerCells': count(owner_cells), 'contextCells': count(graded['context']),
                           'aggregates': count(graded['aggregates'])},
              'aggregates': graded['aggregates'],
              'notPassing': [{'id': i, 'axes': sorted(a for a, v in graded['cells'][i]['axes'].items()
                                                      if v['status'] != 'PASS')} for i in failing]}
    if intrinsic is None:
        result['intrinsicNotGraded'] = count(graded['intrinsic'])
    else:
        result['statuses']['intrinsic'] = count(graded['intrinsic'])
        result['intrinsic'] = graded['intrinsic']
    return result


def intrinsics(owner_config, records):
    """X75 and X76 on the identity candidate, read by the frozen owner engine (DL5o)."""
    config = J.parse(Path(owner_config).read_bytes())
    node = checked(config['node'])
    request = {'config': {'path': str(Path(owner_config).resolve()), 'sha256': sha(owner_config)},
               'records': {'path': str(Path(records).resolve()), 'sha256': sha(records)}}
    result = subprocess.run([str(node), '--import', 'tsx', str(RUNNER)], cwd=CAL, input=json.dumps(request),
                            capture_output=True, text=True, check=False)
    if result.returncode:
        raise ValueError('The frozen-engine intrinsic self-check failed: '+result.stderr[-2000:])
    return J.parse(result.stdout), config


def family_holds(intrinsic):
    """Per position, the names DL5o's admission used: no reading, leaf and family names only."""
    out = {}
    for position, value in sorted((intrinsic.get('X76') or {}).items()):
        holds = value.get('familyHolds') or {}
        applicability = (value.get('applicability') or {}).get('familyHolds') or {}
        out[position] = {'activeAdmitted': sorted(applicability.get('admitted') or {}),
                         'activeRefused': sorted(applicability.get('refused') or {}),
                         'recededAdmitted': sorted(holds.get('admitted') or {}),
                         'recededRefused': sorted(holds.get('refused') or {}),
                         'heldByFamily': holds.get('heldByFamily') or {},
                         'missing': value.get('missing', value.get('missingActive'))}
    return out


def selfcheck(config_path, owner_config=OWNER_CONFIG, records=IDENTITY):
    config = J.parse(Path(config_path).read_bytes())
    union = J.owner_membership(config['ownerUnion'])
    report = J.parse(checked(union['report']).read_bytes())
    contracts = J.parse(checked(config['ownerContracts']).read_bytes())
    inventory = J.parse(checked(config['references']).read_bytes())
    if membership_of(report) != {'cells': union['cells'], 'aggregates': union['aggregates']}:
        raise ValueError('Judge config ownerUnion differs from its prepared report\'s membership')
    intrinsic, engine = intrinsics(owner_config, records)
    result = grade(report, contracts, owner_keys(inventory), union, intrinsic)
    identity = J.parse(Path(records).read_bytes())
    return {'schema': SCHEMA, **result, 'familyHolds': family_holds(intrinsic),
            'config': {'path': rel(config_path), 'sha256': sha(config_path)},
            'preparedReport': union['report'], 'ownerContracts': config['ownerContracts'],
            'inventory': config['references'],
            'identityCandidate': {'records': pin(records), 'cohort': identity['candidateDeclarations'],
                                  'builder': pin(FIT/'owner/r3/identity.py')},
            'engine': {'ownerConfig': pin(owner_config), 'frozenSourceClosure': engine['frozenSourceClosure'],
                       'sourcePins': engine['sourcePins'], 'bridge': pin(BRIDGE), 'runner': pin(RUNNER),
                       'function': 'selfcheckIntrinsics'},
            'grader': {'path': rel(HERE/'live.py'), 'sha256': sha(HERE/'live.py'),
                       'function': 'grade_owner_report'}}


def main(argv):
    def option(name, default):
        nonlocal argv
        if name not in argv: return default
        index = argv.index(name); value = Path(argv[index+1]); argv = argv[:index]+argv[index+2:]
        return value
    write = option('--write', None)
    owner_config = option('--owner-config', OWNER_CONFIG)
    records = option('--records', IDENTITY)
    config = Path(argv[0]).resolve() if argv else HERE/'config.json'
    result = selfcheck(config, owner_config, records)
    raw = (json.dumps(result, indent=1, allow_nan=False)+'\n').encode()
    if write is not None:
        with write.open('xb') as handle: handle.write(raw)
    sys.stdout.write(raw.decode())
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
