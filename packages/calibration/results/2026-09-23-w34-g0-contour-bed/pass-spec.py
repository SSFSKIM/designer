#!/usr/bin/env python3
"""Derive the exact W34 capture pass and price from the pinned declaration."""
import argparse
import copy
import json
from pathlib import Path
from wave import default_wave, native_only


def derive(pose,scale):
    wave=default_wave();doc=copy.deepcopy(wave.spec)
    expected={f'apple-macos-27.0-{s}x-{c}-standard-glass0.5' for s in [1,2] for c in ['light','dark']}
    if {p['key'] for p in doc['profiles']}!=expected:raise ValueError('unexpected W34 profile keys')
    state='rest' if pose=='active' else 'inactive'
    doc['scenes']=[s for s in doc['scenes'] if s['state']==state]
    ids={s['id'] for s in doc['scenes']}
    doc['profiles']=[p for p in doc['profiles'] if f'-{scale}x-' in p['key']]
    for p in doc['profiles']:
        p['scenes']=[s for s in p['scenes'] if s in ids]
        if p['a11y']!='standard':raise ValueError('only standard profiles are declared')
    doc['split']={'calibration':[],'validation':[],'holdout':[],'probe':sorted(ids)}
    return doc


def plan():
    rows=[];wave=default_wave()
    for scale in [1,2]:
        for pose in ['active','inactive']:
            doc=derive(pose,scale)
            cells=[p['key']+'/'+s for p in doc['profiles'] for s in p['scenes']]
            trims=[]
            for cell in cells:
                sid=cell.split('/',1)[1];s=wave.scenes[sid];c=s['component'];b=s['background']
                if c.startswith(('circular-160','continuous-160')) or b.startswith('gradient-135-') or b.startswith('local-y-'):
                    trims.append(cell)
            rows.append(dict(pose=pose,scale=scale,profiles=[p['key'] for p in doc['profiles']],
                cells=cells,cellsPerRun=len(cells),runs=7,secondsPerCell=9.5,
                estimatedSeconds=len(cells)*7*9.5,
                trimTo120=dict(droppedCells=trims,remaining=len(cells)-len(trims),
                    lostAxes='Second radius, 135-degree gradients and both y-edge local-colour contrasts, including their controls/references. Not recommended without a parent ruling.')))
    return dict(passes=rows,totalCellsPerRound=sum(r['cellsPerRun'] for r in rows),
        mainSeconds=sum(r['estimatedSeconds'] for r in rows),
        sentinel=dict(scenes=['grey-128__circular-120','checkerboard__circular-120'],
            extraRuns=3,cellsPerPass=4,passes=4,initialSettleSeconds=8,orderSeed=3401,
            extraSeconds=3*4*4*(9.5+8-1.75)),
        note='Seven runs discover states, not precision. Prices use W29 9.5s/cell; exclude user waiting, mode changes and dry rehearsals. The 120-cell trim is a named alternative, not applied.')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['plan','spec'])
    ap.add_argument('--pose',choices=['active','inactive']);ap.add_argument('--scale',type=int,choices=[1,2])
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    if args.action=='plan':value=plan()
    else:
        if args.pose is None or args.scale is None:ap.error('spec needs --pose and --scale')
        value=derive(args.pose,args.scale)
    text=json.dumps(value,indent=2)+'\n'
    if args.out:
        if args.out.exists():raise ValueError('refuse to overwrite a declared artifact')
        args.out.write_text(text)
    else:print(text,end='')


if __name__=='__main__':main()
