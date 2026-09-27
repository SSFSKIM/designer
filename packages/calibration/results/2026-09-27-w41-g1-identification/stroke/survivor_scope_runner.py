"""Conditional fresh scope: M1 light inactive only; M2 both inactive endpoints.

This entry refuses launch until the parent-relayed certificate review receipt is
committed. It does not manufacture completed M0 or M1-dark optimizer outcomes:
those model-endpoint budgets end at their independently verified certificates.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import resource
import inactive_runner as prior
import start_partition

r = prior.r


def verify_authority():
    path = prior.PRIMARY/'survivor-scope-launch-authority.json'
    raw = path.read_bytes()
    relative = path.relative_to(runner_root())
    committed = subprocess.check_output(['git', '-C', str(runner_root()), 'show', 'HEAD:'+str(relative)])
    if raw != committed:
        raise ValueError('launch authority is not committed at these bytes')
    record = json.loads(raw)
    if not record['m0BothInactiveReviewed'] or not record['m1DarkInactiveReviewed'] \
            or not record['parentM1ReviewRelayReceived']:
        raise ValueError('both verified reviews and parent relay required before scope change')
    for row in record['certificates']:
        if hashlib.sha256((prior.PRIMARY/row['path']).read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('reviewed certificate bytes changed')
    return record


def runner_root():
    return prior.PRIMARY.parents[4]


def observations_for(family, inactive):
    if family not in ('M1', 'M2'):
        raise ValueError('only models outside the complete M0 rejection run here')
    if any(o['role'] != 'calibration' or o['endpoint'] not in (1, 3) for o in inactive):
        raise PermissionError('only admitted inactive calibration may fit')
    return [o for o in inactive if family == 'M2' or o['endpoint'] == 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--partition', required=True, type=int, choices=range(3))
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    authority = verify_authority()
    output = Path(args.out).resolve()
    if prior.PRIMARY not in output.parents:
        raise ValueError('output must stay beneath stroke/')
    output.mkdir(exist_ok=False)
    r.verify_seal()
    indices = list(range(args.partition, 16, 3))
    prior.write(output/'execution.json', dict(partition=args.partition, indices=indices, seed=4100,
        authority=authority, scope={'M1': ['light-inactive'], 'M2': ['light-inactive', 'dark-inactive']},
        heldRevision='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78',
        qualification='Fresh endpoint-authority deviation; unchanged vector, starts, law and budgets',
        sourceSha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in [Path(__file__), Path(start_partition.__file__), Path(r.f.__file__)]}))
    started = time.perf_counter()
    preparation = r.Preparation()
    inactive = prior.load_inactive(preparation, 'calibration')
    prior.write(output/'calibration-admission.json', [dict(cell=o['cell'], endpoint=o['endpoint'],
        scale=o['scale'], pixels=len(o['target']), stateMembership=o['stateMembership']) for o in inactive])
    for family in ('M1', 'M2'):
        observations = observations_for(family, inactive)
        for geometry in ('device', 'css', 'curvature'):
            for index in indices:
                fit, provenance = start_partition.partition(r.f.fit_local, [index])
                t = time.perf_counter()
                print(json.dumps(dict(event='start', family=family, geometry=geometry,
                    index=index, cells=len(observations), seconds=t-started)), flush=True)
                with r.compact_forward():
                    result = fit(observations, family, geometry == 'css', geometry == 'curvature')
                if len(result['starts']) != 1 or result['starts'][0]['startIndex'] != index:
                    raise ValueError('original start identity changed')
                result.update(partitionProvenance=provenance, seconds=time.perf_counter()-t,
                    fittedEndpoints=['light-inactive'] if family == 'M1' else ['light-inactive', 'dark-inactive'],
                    dummyEndpoints=['light-active', 'dark-active', 'dark-inactive'] if family == 'M1'
                                   else ['light-active', 'dark-active'],
                    authority='fresh surviving model-endpoint scope under explicit parent deviation')
                prior.write(output/f'{geometry}-{family}-start-{index:02d}.json', result)
                print(json.dumps(dict(event='completed', family=family, geometry=geometry,
                    index=index, seconds=result['seconds'])), flush=True)
    prior.write(output/'complete.json', dict(seconds=time.perf_counter()-started,
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        validationRead=False, holdoutRead=False, expectedOriginalStartIndices=indices))


if __name__ == '__main__':
    main()
