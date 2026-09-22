#!/usr/bin/env python3
"""Reduce G0's recorded cuts into declarations and diagnostic tables (§5.170).

No captures opened. The bound rule is fixed here before any G1 fitting:
mean per-pixel/channel absolute residual, pixel-weighted within each profile,
pose, backdrop-class and side/corner stratum, rounded upward to two significant
figures. Offsets 2–6 remain unrounded per-cell non-regression baselines.
"""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean
from rules import round_up_2sf
HERE=Path(__file__).resolve().parent
D=json.loads((HERE/'referee.json').read_text())
F=json.loads((HERE/'forms.json').read_text())

def read_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


def main():
    strata=defaultdict(list)
    for row in D['stroke']:
        if '27.0' not in row['profile']: continue
        for side, stat in row['offsets'][0]['strata'].items():
            strata[(row['profile'],row['pose'],row['backdropClass'],side)].append(stat)
    bounds=[]
    for key,rows in sorted(strata.items()):
        pixels=sum(r['pixels'] for r in rows)
        value=sum(r['mae']*r['pixels'] for r in rows)/pixels
        signed=[sum(r['signed'][c]*r['pixels'] for r in rows)/pixels for c in range(3)]
        rgb=[sum(r['maeRGB'][c]*r['pixels'] for r in rows)/pixels for c in range(3)]
        bounds.append(dict(profile=key[0],pose=key[1],backdropClass=key[2],side=key[3],
            cells=len(rows),pixels=pixels,mae=value,maeRGB=rgb,signedRGB=signed,bound=round_up_2sf(value)))
    print('B: offset-one absolute RGB residual by stratum, bounds rounded UP to 2sf')
    for row in bounds: print(json.dumps(row))
    print('\nA: nine-backdrop non-holdout per-profile, pose and span')
    for row in D['blackSummary']:
        if '27.0' in row['profile']: print(json.dumps(row))
    print('\nA: pitch ladder, 1x light active span160 (all probe)')
    for row in D['black']:
        if row['profile']=='apple-macos-27.0-1x-light-standard-glass0.5' and row['span']==160 and row['pose']=='rest':
            print(row['scene'],json.dumps(row['integer']))
    print('\nNative-only all-role lift inventory (no held-out WEB pixels read)')
    native=[]
    for profile in sorted({r['profile'] for r in D['nativeLiftInventory']}):
        rows=[r for r in D['nativeLiftInventory'] if r['profile']==profile]
        row=dict(profile=profile,cells=len(rows),nonzeroCells=sum(r['nonzero']>0 for r in rows),
                 pixels=sum(r['pixels'] for r in rows),nonzeroPixels=sum(r['nonzero'] for r in rows))
        native.append(row); print(json.dumps(row))
    print('\nConditionality: same scene/pose, straight sides separated from corner arcs')
    conditional=[]
    for r in D['stroke']:
        if '27.0' not in r['profile'] or r['background'] not in ('photo','light-solid'): continue
        sides=r['offsets'][0]['strata']; straight=r['offsets'][0]['straight']
        corners=[v for k,v in sides.items() if k.startswith('corner-')]
        npix=sum(v['pixels'] for v in corners)
        row=dict(profile=r['profile'],scene=r['scene'],span=r['span'],nativeNotch=r['nativeNotch'],
            straightSigned=mean(straight['signed']) if straight else None,
            cornerSigned=sum(mean(v['signed'])*v['pixels'] for v in corners)/npix,
            sideSigned={k:mean(v['signed']) for k,v in sides.items()})
        conditional.append(row); print(json.dumps(row))
    print('\nOffsets 2–6 straight and whole-shell signed mean extrema (non-holdout)')
    offsets=[]
    for r in D['stroke']:
        if '27.0' not in r['profile']: continue
        for off in r['offsets'][1:]:
            offsets.append(dict(profile=r['profile'],scene=r['scene'],offset=off['offset'],
                                signed=mean(off['straight']['signed']),shellSigned=mean(off['all']['signed']),
                                mae=off['all']['mae']))
    for key in ('signed','shellSigned','mae'):
        print(key,'min',min(offsets,key=lambda r:r[key]),'max',max(offsets,key=lambda r:r[key]))
    b3=read_module('b3',HERE.parent/'2026-09-21-w32-g2-landing/b3-stop.py')
    b3rows=b3.cells_of(HERE.parent/'2026-09-21-w32-g2-landing/exterior-cut.json')
    inactive=[r for r in b3rows if r['state']=='inactive']
    stops=dict(b3=b3.window(b3rows),b3Bound=b3.B3_BOUND,whole=b3.whole(b3rows),
               inactiveAdmitted=b3.window(inactive),inactiveWhole=b3.whole(inactive))
    print('\nStops',stops)
    m2=[dict(profile=r['profile'],scene=r['scene'],interiorRingPixels=r['nativeInteriorRingPixels'],
             changedByOutside=0,changedByInside=r['forms'][1]['changedInteriorPixels']) for r in F['rows'] if r['m2']]
    print('\nM2 intersection: native-derived mask, held fixed; all 26 cells')
    for r in m2: print(json.dumps(r))
    print('\nFour forms',json.dumps(F['summary']))
    out=dict(rule='pixel-weighted mean absolute RGB per profile/pose/backdrop/side, ceil 2sf',
             bounds=bounds,nativeLift=native,conditionality=conditional,stops=stops,m2=m2)
    (HERE/'tables.json').write_text(json.dumps(out,indent=2)+'\n')

if __name__=='__main__': main()
