#!/usr/bin/env python3.12
"""Read W33 G1b's stops without a holdout pixel (§5.172).

G0's integer and analytic black-floor masks are imported, not approximated.
C1 uses the cut's complete admitted-band T and its upper-middle statistic.
B3 uses W32 G2's population and functional. Thin compares every cell and band
with this gate's fresh shipped-byte reproduction, including accessibility.
The halo diagnostic substitutes non-holdout checkerboard-8 for the original
held-out checkerboard; its 137.10 archival maximum is not a fitted objective.
"""
import argparse
from collections import defaultdict
import importlib.util
import json
import os
from pathlib import Path
from statistics import mean
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
ROOT = CAL.parent.parent
G0 = CAL / 'results/2026-09-22-w33-g0-rim-cut'
G2 = CAL / 'results/2026-09-21-w32-g2-landing'
sys.path.insert(0, str(G0))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def upper(values):
    return sorted(values)[len(values)//2] if values else None


def lab(rgb):
    x = rgb / 255
    x = np.where(x <= .04045, x/12.92, ((x+.055)/1.055)**2.4)
    lms = x @ np.array([[.4122214708,.5363325363,.0514459929],
                        [.2119034982,.6806995451,.1073969566],
                        [.0883024619,.2817188376,.6299787005]]).T
    return np.cbrt(lms) @ np.array([[.2104542553,.793617785,-.0040720468],
                                  [1.9779984951,-2.428592205,.4505937099],
                                  [.0259040371,.7827717662,-.808675766]]).T


def main():
    p = argparse.ArgumentParser()
    p.add_argument('label')
    p.add_argument('--scratch', type=Path, default=Path('/tmp/w33-g1b-fit'))
    p.add_argument('--against', default='pre-fit')
    a = p.parse_args()
    source = a.scratch/a.label
    out = HERE/'rounds'/a.label
    out.mkdir(parents=True, exist_ok=False)
    raw = json.loads((source/'matrix.json').read_text())
    declared = {(r['profile'],r['scene'],r['renderer']) for r in json.loads(
        (HERE/'declared-bed.json').read_text())['rows']
        if r['renderer']=='webgpu' and r['role']!='holdout'}
    key = lambda c: (c['key']['profileKey'],c['key']['sceneId'],c['key']['web']['renderer'])
    selected = [c for c in raw['cells'] if key(c) in declared]
    assert len(selected)==len(declared)==386
    diagnostic = [key(c) for c in raw['cells'] if key(c) not in declared]
    raw['cells'] = selected
    (source/'declared-matrix.json').write_text(json.dumps(raw)+'\n')
    with (out/'exterior-cut.txt').open('w') as f:
        subprocess.run([sys.executable, str(HERE/'exterior-cut.py'), '--matrix',
                        str(source/'declared-matrix.json'), '--at-documents', 'any', '--out', str(out)],
                       check=True, stdout=f)
    cut = json.loads((out/'exterior-cut.json').read_text())
    rows = cut['rows']
    assert not cut['withHoldout'] and all(r['set'] != 'holdout' for r in rows)
    result = dict(label=a.label, matrix=str(source/'matrix.json'), documents=cut['documents'],
                  diagnosticOnlyRows=diagnostic)
    active = [r for r in rows if r['tier']=='webgpu' and r['state']!='inactive']
    c1 = []
    for bed in ('1x light','2x light','1x dark','2x dark'):
        for span in (96,128,160):
            rs = [r for r in active if r['bed']==bed and r['span']==span
                  and r['T'] is not None and r['bandsUsed']==r['admitted']]
            value = upper([r['T'] for r in rs])
            assert value is not None
            c1.append(dict(bed=bed, span=span, cells=len(rs), value=value, passStop=value<=.0042))
    result['C1'] = c1
    b3 = module('w33_b3', G2/'b3-stop.py')
    population = b3.cells_of(out/'exterior-cut.json')
    result['B3'] = dict(bound=b3.B3_BOUND, value=b3.window(population), cells=len(population),
                        passStop=b3.window(population)<=b3.B3_BOUND,
                        wholeExteriorWarning=b3.whole(population), archivalWarning=.0007158135811605964,
                        decomposition=[])
    for name, rs in [('active',[r for r in population if r['state']!='inactive']),
                     ('inactive',[r for r in population if r['state']=='inactive'])] + [
                     (bed,[r for r in population if r['bed']==bed]) for bed in sorted({r['bed'] for r in population})]:
        result['B3']['decomposition'].append(dict(population=name, cells=len(rs),
                                                value=b3.window(rs), whole=b3.whole(rs)))
    reference = rows if a.label == a.against else json.loads(
        (HERE/'rounds'/a.against/'exterior-cut.json').read_text())['rows']
    before = {(r['profile'],r['scene'],r['tier']):r for r in reference}
    thin, bands = [], defaultdict(list)
    for r in active:
        entry = r['perBand']['all'].get('3-6')
        if entry and entry['deltaA'] is not None:
            bands[(r['bed'],r['span'])].append(entry['deltaA'])
        if r['span'] not in (32,44) or r['T'] is None:
            continue
        prev = before[(r['profile'],r['scene'],r['tier'])]
        for band in ('3-6','6-12'):
            v, v0 = r['perBand']['all'].get(band), prev['perBand']['all'].get(band)
            if not v or v['deltaA'] is None:
                continue
            value, was = abs(v['deltaA']), abs(v0['deltaA'])
            thin.append(dict(profile=r['profile'],scene=r['scene'],bed=r['bed'],span=r['span'],
                             band=band,before=was,value=value,move=value-was,
                             passStop=value-was<=.002044))
    result['thin'] = thin
    result['thinOrderStatistics'] = []
    for bed,span,band in sorted({(r['bed'],r['span'],r['band']) for r in thin}):
        rs = [r for r in thin if (r['bed'],r['span'],r['band'])==(bed,span,band)]
        was,value = upper([r['before'] for r in rs]),upper([r['value'] for r in rs])
        result['thinOrderStatistics'].append(dict(bed=bed,span=span,band=band,
                                                  before=was,value=value,passStop=value<=was))
    result['band3to6'] = [dict(bed=k[0],span=k[1],cells=len(v),signedUpperMiddle=upper(v),
                              absoluteUpperMiddle=upper([abs(x) for x in v]), min=min(v), max=max(v))
                          for k,v in sorted(bands.items())]
    constants = json.loads((source/'constants.json').read_text()) if (source/'constants.json').exists() else {
        scheme:json.loads((CAL/'profiles'/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json').read_text())['patch']['outerShadow']
        for scheme in ('light','dark')}
    windows = {'light':[(8.8966,9.0193),(12.6397,13.7947),(16.7033,17.8198)],
               'dark':[(8.9084,9.3180),(12.7458,13.8499),(16.7931,18.3237)]}
    result['B1'] = []
    for scheme,c in constants.items():
        for span,(lo,hi) in zip((96,128,160),windows[scheme]):
            sigma = c['sigmaPx']+max(c['sigmaThinOffsetPx'],c['sigmaSlopePerSpan']*(span-c['sigmaSpanRefPx']))
            result['B1'].append(dict(scheme=scheme,span=span,sigma=sigma,window=[lo,hi],passStop=lo<=sigma<=hi))
    (out/'constants.json').write_text(json.dumps(constants,indent=2)+'\n')
    with (out/'anchor-solve.txt').open('w') as f:
        subprocess.run([sys.executable,str(HERE/'anchor-solve.py'),str(out/'exterior-cut.json'),
                        '--constants',str(out/'constants.json'),'--label',a.label],check=True,stdout=f)
    referee = module('w33_referee',G0/'referee.py')
    baseline = [r for r in json.loads((G0/'referee.json').read_text())['black'] if '27.0' in r['profile']]
    assert len(baseline)==232
    black = []
    for prev in baseline:
        profile, scene = prev['profile'], prev['scene']
        assert referee.ROLES[scene] not in ('holdout','recorded')
        n = referee.rgb(referee.FIXTURES/profile/(scene+'.png'))
        w = referee.rgb(source/'captures'/profile/scene/(scene+'__webgpu.png'))
        h,width = n.shape[:2]; scale=width/320
        b = referee.rgb(referee.FIXTURES/'backgrounds'/f'{prev["background"]}@{scale:g}x.png')
        rect,_,_ = referee.geometry(scene,scale)
        integer,analytic = referee.exterior_masks(width,h,rect,scale)
        row = {k:v for k,v in prev.items() if k not in ('integer','analytic')}
        row.update(integer=referee.black_read(n,w,b,integer),analytic=referee.black_read(n,w,b,analytic))
        row['aboveOneNonRegression'] = row['integer']['aboveOne']<=prev['integer']['aboveOne']
        black.append(row)
    result['black'] = black
    result['blackSummary'] = referee.summarize_black(black)
    result['halo'] = []
    for scale in (1,2):
        profile=f'apple-macos-27.0-{scale}x-light-standard-glass0.5'
        for pose in ('rest','inactive'):
            scene=f'checkerboard-8__rrect-lg__{pose}'
            assert referee.ROLES[scene]=='probe'
            n=referee.rgb(referee.FIXTURES/profile/(scene+'.png'))
            w=referee.rgb(source/'captures'/profile/scene/(scene+'__webgpu.png'))
            rect,_,_=referee.geometry(scene,scale)
            y,x=np.mgrid[:n.shape[0],:n.shape[1]]
            x0,y0,x1,y1=rect
            mask=~((x>=(x0-12*scale))&(x<(x1+12*scale))&(y>=(y0-12*scale))&(y<(y1+12*scale)))
            diff=np.minimum(255,np.linalg.norm(lab(n)-lab(w),axis=2)*8*255)[mask]
            result['halo'].append(dict(profile=profile,scene=scene,pixels=int(mask.sum()),
                                       mean=float(diff.mean()),max=float(diff.max()),belowArchival137_10=float(diff.max())<137.10))
    (out/'stops.json').write_text(json.dumps(result,indent=1)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('thin','black')},indent=2))
    print('thin',len(thin),'failures',sum(not r['passStop'] for r in thin),'largest increase',max(r['move'] for r in thin))
    print('black',len(black),'nonzero',sum(r['integer']['aboveZero'] for r in black),
          'aboveOne',sum(r['integer']['aboveOne'] for r in black))


if __name__ == '__main__':
    main()
