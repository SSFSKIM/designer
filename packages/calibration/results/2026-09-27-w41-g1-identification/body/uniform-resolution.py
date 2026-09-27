"""Recheck light-inactive E3/EH6 resolution on the complete uniform transfer union."""
import argparse
import gzip
import json
from pathlib import Path
import numpy as np
import replay

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('transfer', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
scores = json.loads(gzip.decompress((a.transfer / 'scores.json.gz').read_bytes()))
summary = json.loads((a.transfer / 'summary.json').read_text())
for family in ['E3', 'EH6']:
    e = next(e for e in summary['endpoints'] if e['family'] == family and e['endpoint'] == 'light-inactive')
    assert 'globalMinimax' in e['survivingMethods']
by_family = {f: {(r['cell'], r['member']): r for r in scores if r['family'] == f and
             r['endpoint'] == 'light-inactive' and r['method'] == 'globalMinimax'} for f in ['E3', 'EH6']}
assert by_family['E3'].keys() == by_family['EH6'].keys()
comparisons = []
for key, x in sorted(by_family['E3'].items()):
    y = by_family['EH6'][key]
    observed = np.array(x['nativeRGB'])
    measured = (observed > 5) & (observed < 250)
    delta = abs(np.array(x['predictedRGB']) - y['predictedRGB'])
    threshold = np.maximum(3, np.array(x['barRGB']) + y['barRGB'])
    for j in np.flatnonzero(measured):
        comparisons.append(dict(cell=key[0], member=key[1], channel='RGB'[j],
            separationCodes=float(delta[j]), thresholdCodes=float(threshold[j])))
separators = [r for r in comparisons if r['separationCodes'] >= r['thresholdCodes']]
replay.save(a.output, dict(scope='all admitted calibration/validation uniform glass members',
    endpoint='light-inactive', families=['E3', 'EH6'], method='globalMinimax',
    cells=len({k[0] for k in by_family['E3']}), members=len(by_family['E3']),
    measuredComparisons=len(comparisons), maximum=max(comparisons, key=lambda r: r['separationCodes']),
    admittedSeparators=separators, verdict='insufficient resolution' if not separators else 'resolved instances',
    scopeQualification='Fixed surviving endpoint instances, not complete four-endpoint survivors or universal family separation',
    sources={str(path.resolve()): replay.digest(path) for path in
             [Path(__file__), a.transfer / 'scores.json.gz', a.transfer / 'summary.json']}))
