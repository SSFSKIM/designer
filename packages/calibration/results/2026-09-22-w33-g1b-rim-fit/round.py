#!/usr/bin/env python3.12
"""Render one lift/anchor candidate on the declared non-holdout bed (§5.172).

A uses shipped anchors. B uses A's closed-form window solve, rounded to the
four-decimal precision of the shipped anchors. No other leaf can enter a round.
All sets for one profile share one browser invocation and one X6 attestation.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parent.parent
ALLOWED = {'liftAmplitude','thickOcclusionAt96','thickOcclusionAt128','thickOcclusionAt160'}


def load(name, path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m
    spec.loader.exec_module(m)
    return m


def main():
    p=argparse.ArgumentParser()
    p.add_argument('label')
    p.add_argument('--solve',help='prior round whose window departure determines the anchors')
    p.add_argument('--repeat',help='repeat an unchanged candidate instead of fitting')
    p.add_argument('--scratch',type=Path,default=Path('/tmp/w33-g1b-fit'))
    a=p.parse_args()
    assert not (a.solve and a.repeat)
    dest=a.scratch/a.label
    dest.mkdir(parents=True,exist_ok=False)
    docs=dest/'documents'; docs.mkdir()
    originals={s:json.loads((CAL/'profiles'/f'apple-macos-27.0-1x-{s}-standard-glass0.5.json').read_text()) for s in ('light','dark')}
    constants={s:dict(d['patch']['outerShadow']) for s,d in originals.items()}
    for c in constants.values(): c['liftAmplitude']=0
    solve=[]
    if a.solve:
        solver=load('w33_anchor',HERE/'anchor-solve.py')
        prior=HERE/'rounds'/a.solve
        source=json.loads((prior/'exterior-cut.json').read_text())['rows']
        previous=json.loads((prior/'constants.json').read_text())
        for scheme in constants:
            for span in (96,128,160):
                regime='thick'+str(span)
                rs=[r for r in source if r['scheme']==scheme and r['state']!='inactive'
                    and r['tier']=='webgpu' and r['set']!='holdout'
                    and r['bed'] in solver.STANDARD_BEDS[scheme]
                    and solver.regime(r['span'],r['backdrop'])==regime
                    and r['departure']['window']['native'] is not None]
                n=sum(r['departure']['window']['native'] for r in rs)/len(rs)
                w=sum(r['departure']['window']['web'] for r in rs)/len(rs)
                leaf='thickOcclusionAt'+str(span)
                before=previous[scheme][leaf]
                wanted=before*n/w
                constants[scheme][leaf]=round(wanted,4)
                solve.append(dict(scheme=scheme,span=span,cells=len(rs),native=n,web=w,
                                  ratio=n/w,before=before,wanted=wanted,rounded=round(wanted,4)))
    if a.repeat:
        constants=json.loads((HERE/'rounds'/a.repeat/'constants.json').read_text())
    for scheme,original in originals.items():
        base=original['patch']['outerShadow']
        assert set(base)==set(constants[scheme])
        changed={k for k in base if base[k]!=constants[scheme][k]}
        assert changed<=ALLOWED and constants[scheme]['liftAmplitude']==0
        original['patch']['outerShadow']=constants[scheme]
        name=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
        (docs/name).write_text(json.dumps(original,indent=2)+'\n')
        receded=name.replace('.json','-receded.json')
        rec=json.loads((CAL/'profiles'/receded).read_text())
        assert all(rec['patch']['outerShadow'][k]==0 for k in ALLOWED)
        shutil.copyfile(CAL/'profiles'/receded,docs/receded)
    (dest/'constants.json').write_text(json.dumps(constants,indent=2)+'\n')
    (dest/'solve.json').write_text(json.dumps(solve,indent=2)+'\n')
    x6=load('w33_capture',HERE/'render-bed.py').x6
    selected=[r for r in json.loads((HERE/'declared-bed.json').read_text())['rows']
              if r['renderer']=='webgpu' and r['role']!='holdout']
    assert len(selected)==386
    for profile in dict.fromkeys(r['profile'] for r in selected):
        scheme='dark' if '-dark-' in profile else 'light'
        document=docs/f'apple-macos-27.0-1x-{scheme}-standard-glass0.5.json'
        receded=document.with_name(document.stem+'-receded.json')
        ids=sorted({r['scene'] for r in selected if r['profile']==profile})
        x6(f'{a.label}/{profile}/declared-fit-bed')
        subprocess.run(['npx','tsx','cli/compare.ts','--profile',profile,
                        '--material-profile',str(document),'--receded-profile',str(receded),
                        '--renderer','webgpu','--alpha','--write-partial',
                        '--out-matrix',str(dest/'matrix.json'),'--set','calibration,validation,probe',
                        '--scene',','.join(ids)],cwd=CAL,
                       env=dict(os.environ,VITREA_WEB_CAPTURES=str(dest/'captures')),check=True)
    with (HERE/(a.label+'-stops.txt')).open('w') as f:
        subprocess.run([sys.executable,str(HERE/'read-round.py'),a.label],check=True,stdout=f)
    print('complete',dest)


if __name__=='__main__': main()
