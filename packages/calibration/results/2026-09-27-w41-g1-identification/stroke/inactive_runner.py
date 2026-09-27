"""Fresh inactive-endpoint authority under the explicit parent scope deviation.

Three seed-index partitions may execute concurrently; each reconstructs the
original16starts and skips only other partitions' indices. Every original start
retains all sealed solver and width-search budgets. Results are written after
each completed start, with active dummy slots explicitly uninterpretable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

PRIMARY = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
PROOF_STROKE = PROOF/'packages/calibration/results/2026-09-27-w41-g1-identification/stroke'
sys.path.insert(0, str(PROOF_STROKE))
import replay as r
# New orchestration is read from the primary tree; held law and fitter stay the
# byte-pinned proof-tree modules already imported above.
sys.path.remove(str(PROOF_STROKE))
import start_partition


def write(path, value):
    with path.open('x') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def load_inactive(preparation, role):
    native, wave, reader = r.guarded_reader((role,))
    result = []
    for (cell, kind), entry in sorted(reader.entries.items()):
        sid = cell.split('/', 1)[1]
        if kind != 'crop' or sid not in reader.allowed or not entry['admitted']:
            continue
        if not sid.endswith('__inactive') or native.wave.native_only(wave.component(sid)):
            continue
        runs, states = native.archive.unbundle(reader.read(cell, 'crop'))
        runs = [v for v in runs if v['admitted'] and v['protocol'] == 'normal']
        payloads = {s: native.archive.unpack(states[s]) for s in {v['state'] for v in runs}}
        observation = preparation.prepare(cell, role, [payloads[v['state']] for v in runs],
            [v['state'] for v in runs], wave.scenes[sid]['background'])
        if observation['endpoint'] not in (1, 3):
            raise ValueError('active observation entered inactive authority')
        result.append(observation)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--partition', type=int, required=True, choices=range(3))
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    output = Path(args.out).resolve()
    if PRIMARY not in output.parents:
        raise ValueError('output must be beneath primary stroke evidence')
    output.mkdir(exist_ok=False)
    r.verify_seal()
    indices = list(range(args.partition, 16, 3))
    write(output/'execution.json', dict(partition=args.partition, indices=indices, seed=4100,
        proofRoot=str(PROOF), heldRevision='d35b4cbf43f1fcdda55063b3b8e0fa178d720a78',
        authority='inactive endpoint candidate, explicitly promoted by parent; LOCAL fitter',
        activeCoordinates='unobserved dummy slots; not interpreted, fitted to observations or borrowed',
        declarationSha256=r.DECLARATION_SHA, previousInactiveDiagnostic='NOT RUN',
        sourceSha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                      [Path(__file__), Path(start_partition.__file__), Path(r.f.__file__)]}))
    started = time.perf_counter()
    preparation = r.Preparation()
    observations = load_inactive(preparation, 'calibration')
    write(output/'calibration-admission.json', [dict(cell=o['cell'], endpoint=o['endpoint'],
        scale=o['scale'], pixels=len(o['target']), stateMembership=o['stateMembership'])
        for o in observations])
    print(json.dumps(dict(event='prepared', cells=len(observations),
        seconds=time.perf_counter()-started,
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)), flush=True)
    if any(o['role'] != 'calibration' for o in observations):
        raise PermissionError('fit accepts calibration only')
    for family in ('M0', 'M1', 'M2'):
        for geometry in ('device', 'css', 'curvature'):
            for index in indices:
                fit, partition_provenance = start_partition.partition(r.f.fit_local, [index])
                t = time.perf_counter()
                print(json.dumps(dict(event='start', family=family, geometry=geometry,
                    index=index, seconds=t-started)), flush=True)
                with r.compact_forward():
                    result = fit(observations, family, geometry == 'css', geometry == 'curvature')
                if len(result['starts']) != 1 or result['starts'][0]['startIndex'] != index:
                    raise ValueError('partition changed original start identity')
                result['partitionProvenance'] = partition_provenance
                result['seconds'] = time.perf_counter()-t
                result['activeCoordinates'] = 'unidentifiable dummy slots; omit from interpretation'
                result['authority'] = 'inactive-only candidate under recorded parent deviation'
                write(output/f'{geometry}-{family}-start-{index:02d}.json', result)
                print(json.dumps(dict(event='completed', family=family, geometry=geometry,
                    index=index, seconds=result['seconds'])), flush=True)
    write(output/'complete.json', dict(seconds=time.perf_counter()-started,
        peakRSSBytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        validationRead=False, holdoutRead=False, expectedOriginalStartIndices=indices))


if __name__ == '__main__':
    main()
