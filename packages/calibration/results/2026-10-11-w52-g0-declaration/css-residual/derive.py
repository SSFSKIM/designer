"""Record the measured old CSS level gap that W52's explicit decline retains.

This reduces committed exposed W51 CURRENT operands, not W51 candidate values,
new pixels or a W52 candidate. Every projected scalar is checked against the
hash-bound original report. A future W52 read still checks CSS growth/coherence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
W51 = CAL / 'results/2026-10-10-w51-regate/evidence'
INPUTS = {
    'report': (W51 / 'gate-dl6-complete/report.json',
               'af06fec2d652264e3e44c52d483b12dbf8b64a0de4206dba7bb9b1db0edaf128'),
    'projection': (W51 / 'gate-dl6/gains-and-unseen-numeric.json',
                   '732604137f485e01ae1b8818a7e68ab515eefaa13bde2943af15df877bbdcfba'),
}


def derive():
    values = {}
    for name, (path, expected) in INPUTS.items():
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f'Changed historical CSS evidence: {name}')
        values[name] = json.loads(raw)
    report, projection = values['report'], values['projection']
    if projection['sourceReport']['sha256'] != INPUTS['report'][1]:
        raise ValueError('Projection names another gate report')
    by_key = {tuple(c[k] for k in ('profile', 'renderer', 'scene', 'statistic')): c
              for c in report['cells']}
    groups = []
    for group in projection['gains']:
        if group['renderer'] != 'css':
            continue
        components = []
        for item in group['components']:
            reading = by_key[tuple(item['key'])]['readings'][item['substatistic']]
            channel = None if item['component'] is None else 'RGB'.index(item['component'])
            operands = {}
            for label in ('native', 'current'):
                value = reading[label] if channel is None else reading[label][channel]
                if not math.isfinite(value) or value != item[label]:
                    raise ValueError('Projected current/native scalar does not match report')
                operands[label] = value
            components.append({k: item[k] for k in ('key', 'substatistic', 'component')} |
                              operands | {'absoluteErrorCodes': abs(operands['current'] - operands['native'])})
        errors = [c['absoluteErrorCodes'] for c in components]
        maximum, mean = max(errors), sum(errors) / len(errors)
        if (maximum != group['currentMaximumAbsoluteError'] or
                mean != group['currentMeanAbsoluteError']):
            raise ValueError('Historical CSS aggregate does not reproduce')
        groups.append({k: group[k] for k in ('kind', 'position', 'pose', 'renderer',
                       'physicalCount', 'statisticKeys', 'scalarComponents')} |
                      {'maximumAbsoluteErrorCodes': maximum, 'meanAbsoluteErrorCodes': mean,
                       'components': components})
    if len(groups) != 12:
        raise ValueError('Expected three measured CSS level families at four endpoints')
    return {'schema': 'w52-css-decline-residual-1', 'status': 'HISTORICAL_CURRENT_MEASURED',
            'meaning': 'Measured current CSS gaps retained by the declared W52 decline; '
                       'not a new W52 render or acceptance result.',
            'rule': 'No new CSS level-error growth beyond one code; unchanged coherence scope.',
            'inputs': {k: {'path': str(p.relative_to(CAL)), 'sha256': sha}
                       for k, (p, sha) in INPUTS.items()},
            'groups': groups}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    result = derive()
    raw = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
    path = HERE / 'current-gap.json'
    if args.check:
        if path.read_bytes() != raw:
            raise ValueError('CSS residual projection differs')
    else:
        path.write_bytes(raw)
    for g in result['groups']:
        print(f"{g['kind']} glass{g['position']} {g['pose']}: "
              f"max {g['maximumAbsoluteErrorCodes']:.6f}, "
              f"mean {g['meanAbsoluteErrorCodes']:.6f} codes")
