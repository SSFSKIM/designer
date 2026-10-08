"""Replay W49b's path-defined diagnosis on this checkout and price a low-end hypothesis.

No render and no fit: the prediction is the W9 full-authority algebra with an encoded
straight line between black and the already observed [28,28,30] body level. That mixed-RGB
anchor is only an illustrative scalar proxy, not a new native neutral-28 measurement.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = HERE.parent / '2026-10-08-w49b-g0-declaration/diagnostics/black-level'
spec = importlib.util.spec_from_file_location('w49b_black_level', OLD / 'read.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def decode(code):
    x = code / 255
    return x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4


def main():
    reading = D.run(ROOT, Path('/Users/new/Developer/GitHub/designer'))
    # Absolute provenance paths differ after W49b's worktree was removed. Compare the
    # path-free measured and attribution table, not a rewritten historical JSON file.
    assert D.table_csv(reading) == (OLD / 'table.csv').read_bytes()
    output = []
    for cell in reading['cells']:
        if cell['status'] != 'MEASURED_PAIR' or not cell.get('toneAttribution'):
            continue
        if cell['component'] not in ('rrect-ml', 'rrect-lg'):
            continue
        t = cell['toneAttribution'][0]
        support = cell['supports']['deep8_far24' if cell['background'] == 'impulse' else 'deep8']
        row = dict(profile=cell['profile'], scene=cell['scene'], span=cell['spanCss'],
                   pixels=support['pixels'], nativeCodes=support['native']['encodedLumaMeanCodes'],
                   webCodes=support['web']['encodedLumaMeanCodes'], tone=t)
        if cell['background'] == 'impulse':
            zero = 20 if cell['pose'] == 'inactive' else 32
            at28 = 48.1444 if cell['pose'] == 'inactive' else (54.1444 if cell['spanCss'] == 160 else 55.1444)
            x_codes = t['encodedInputX'] * 255
            proxy_target = zero + (at28 - zero) * x_codes / 28.1444
            floor = t['neutralClampContext']['minimumTransmittedAggregateLinear']
            proxy_linear = decode(proxy_target)
            row['illustrativeFullAuthorityPrediction'] = dict(
                targetCodes=proxy_target, targetLinear=proxy_linear,
                transmittedAggregateFloor=floor,
                blackFieldCodes=D.encode(max(0, proxy_linear - floor)) * 255,
                qualification='Not rendered or fitted; neglects nonzero blurred samples, rim and tint. '
                'Straight-line low-end proxy; the native 1–8 response is not measured. '
                'At full authority and zero collapse the black-field intercept is R-(1-alpha)*mu.')
        output.append(row)
    doc = dict(schema='w50-attribution-1', historicalTableReplay='BYTE_IDENTICAL',
               interpreter=sys.version, rows=output)
    (HERE / 'attribution.json').write_text(json.dumps(doc, indent=2) + '\n')
    print('W49b table.csv reproduced byte-for-byte on current checkout; no render.')
    for r in output:
        if 'illustrativeFullAuthorityPrediction' in r:
            print(r['profile'], r['scene'], 'native', round(r['nativeCodes'], 3),
                  'web', round(r['webCodes'], 3), 'hypothesis',
                  round(r['illustrativeFullAuthorityPrediction']['blackFieldCodes'], 3))


if __name__ == '__main__':
    main()
