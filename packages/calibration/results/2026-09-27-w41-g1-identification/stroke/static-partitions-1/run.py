"""Original survivor-scope partition loop with explicit disjoint remaining tasks.

Adaptive admission is retired. The only resource guard is the coordinator's
25-percent kernel level at process launch. Fits retain the original seed vectors,
full budgets, held forward, scoped observations and proven per-fit memo wrapper.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
STROKE = HERE.parent
sys.path.insert(0, str(STROKE))
sys.path.insert(0, str(STROKE/'memoization'))
import survivor_scope_runner as scope
import start_partition
from solver_memo import SolverMemo
prior, r = scope.prior, scope.r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--partition', required=True, choices=('A', 'B'))
    args = ap.parse_args()
    level = int(subprocess.check_output(['/usr/sbin/sysctl', '-n', 'kern.memorystatus_level']))
    if level < 25:
        raise RuntimeError(f'launch refused: kernel memory level {level} below25')
    declaration = json.loads((HERE/'declaration.json').read_text())
    for path, digest in declaration['sourceSha256'].items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest() != digest:
            raise ValueError('source changed: '+path)
    tasks = declaration['partitions'][args.partition]
    out = HERE/args.partition
    out.mkdir(exist_ok=False)
    authority = scope.verify_authority()
    r.verify_seal()
    prior.write(out/'execution.json', dict(partition=args.partition, tasks=tasks,
        seed=4100, authority=authority, launchKernelLevelPercent=level,
        resourcePolicy='adaptive scheduler retired for the remainder',
        declarationSha256=hashlib.sha256((HERE/'declaration.json').read_bytes()).hexdigest(),
        sourceSha256=declaration['sourceSha256']))
    started = time.perf_counter()
    preparation = r.Preparation()
    inactive = prior.load_inactive(preparation, 'calibration')
    prior.write(out/'calibration-admission.json', [dict(cell=o['cell'], endpoint=o['endpoint'],
        scale=o['scale'], pixels=len(o['target']), stateMembership=o['stateMembership'])
        for o in inactive])
    for family, geometry, index in tasks:
        observations = scope.observations_for(family, inactive)
        fit, provenance = start_partition.partition(r.f.fit_local, [index])
        t = time.perf_counter()
        print(json.dumps(dict(event='start', family=family, geometry=geometry,
            index=index, cells=len(observations), seconds=t-started)), flush=True)
        with r.compact_forward(), SolverMemo(r.f, observations, family, geometry == 'curvature') as memo:
            result = fit(observations, family, False, geometry == 'curvature')
        if len(result['starts']) != 1 or result['starts'][0]['startIndex'] != index:
            raise ValueError('original start identity changed')
        result.update(partitionProvenance=provenance, seconds=time.perf_counter()-t,
            fittedEndpoints=['light-inactive'] if family == 'M1' else ['light-inactive', 'dark-inactive'],
            dummyEndpoints=['light-active', 'dark-active', 'dark-inactive'] if family == 'M1'
                           else ['light-active', 'dark-active'],
            authority='fresh surviving model-endpoint scope under explicit parent deviation',
            validationRead=False, holdoutRead=False, memoization=memo.summary(),
            staticPartition=args.partition)
        prior.write(out/f'{geometry}-{family}-start-{index:02d}.json', result)
        print(json.dumps(dict(event='completed', family=family, geometry=geometry,
            index=index, seconds=result['seconds'])), flush=True)
    prior.write(out/'complete.json', dict(seconds=time.perf_counter()-started,
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        validationRead=False, holdoutRead=False, completedTasks=tasks))


if __name__ == '__main__':
    main()
