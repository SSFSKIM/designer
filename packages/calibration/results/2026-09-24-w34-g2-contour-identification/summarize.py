#!/usr/bin/env python3.12
"""Compact indices into per-cell absolute tables; no pooling buys closure."""
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
import identification as M


def read(name):
    raw=(M.HERE/name).read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw)


def label(profile,pose):
    return ('1x' if '-1x-' in profile else '2x')+'/'+('dark' if '-dark-' in profile else 'light')+'/'+('active' if pose=='rest' else pose)


def main():
    heads=read('validation-headlines.json')
    fits=read('fits.json')
    family=[]
    for key in sorted({(h['profile'],h['pose'],h['part'],h['name'],h['space']) for h in heads}):
        rows=[h for h in heads if (h['profile'],h['pose'],h['part'],h['name'],h['space'])==key and h['role']=='validation']
        best=min(rows,key=lambda r:r['worstMAE'])
        family.append(dict(stratum=label(key[0],key[1]),part=key[2],family=key[3],space=key[4],
            bestValidationWorstBin=best['worstMAE'],method=best['method'],fit=best['fit'],
            shellZeroWorstBin=best['shellZeroWorstMAE'],bar=best['maxBar'],tau=1,pixels=best['pixels'],
            bins=best['bins'],underpopulated=best['underpopulated'],status=best['outcome'],
            domain='all shapes' if fits[best['fit']]['spec']['stage']=='W33-first' else 'circular only'))
    M.save(M.HERE/'family-best.json',family)
    with (M.HERE/'family-best.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(family[0]));writer.writeheader();writer.writerows(family)
    native=read('native-notches.json');web=read('web-notches.json')
    wn={(r['cell'],r['part']):r['notch'] for r in web}
    gap=read('web-gap.json.gz');zero=read('native-zero.json.gz')
    rows=[]
    for key in sorted({(r['profile'],r['pose'],r['part']) for r in native}):
        cells=[r for r in native if (r['profile'],r['pose'],r['part'])==key]
        ids={r['cell'] for r in cells}
        gr=[r for r in gap if r['cell'] in ids and r['part']==key[2] and r['admissible']]
        zr=[r for r in zero if r['cell'] in ids and r['part']==key[2] and r['admissible']]
        rows.append(dict(stratum=label(key[0],key[1]),part=key[2],cells=len(cells),
            nativeNotchMedian=float(np.median([r['notch'] for r in cells])),
            webNotchMedian=float(np.median([wn[(r['cell'],key[2])] for r in cells])),
            maxWebGap=max(max(r['maeRGB']) for r in gr),
            maxZeroResidual=max(max(r['maeRGB']) for r in zr),
            shellZeroMaxWebGap=max(max(r['maeRGB']) for r in gr if r['shell']==0),
            bins=len(gr),pixels=sum(r['pixels'] for r in gr),
            maxBar=max(max(r['barRGB']) for r in gr),tau=1))
    M.save(M.HERE/'strata.json',rows)
    print('| stratum | part | native notch | web notch | max native–web | pixels | bar / tolerance |')
    print('| --- | --- | ---: | ---: | ---: | ---: | ---: |')
    for r in rows:
        print(f"| {r['stratum']} | {r['part']} | {r['nativeNotchMedian']:.3f} | {r['webNotchMedian']:.3f} | {r['maxWebGap']:.3f} | {r['pixels']} | {r['maxBar']:.4g} / 1 |")


if __name__=='__main__':main()
