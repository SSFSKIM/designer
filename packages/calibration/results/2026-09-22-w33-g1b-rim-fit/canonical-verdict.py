#!/usr/bin/env python3.12
"""Verify the sealed read against its repeated candidate and read every black cell (§5.172).

This post-seal reader includes holdout only when explicitly requested. It measures
pixels; it fits no parameter. The holdout capture's once-only artifact must exist.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
G0=CAL/'results/2026-09-22-w33-g0-rim-cut'
sys.path.insert(0,str(G0))
spec=importlib.util.spec_from_file_location('w33_canonical_referee',G0/'referee.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
p=argparse.ArgumentParser(); p.add_argument('--include-holdout',action='store_true'); a=p.parse_args()
if a.include_holdout: assert (HERE/'read-holdout-completed.txt').exists()
cells=json.loads((CAL/'results/matrix.json').read_text())['cells']
key=lambda c:(c['key']['profileKey'],c['key']['sceneId'],c['key']['web']['renderer'])
now={key(c):c for c in cells}
rounds=json.loads(Path('/tmp/w33-g1b-fit/B/matrix.json').read_text())['cells']
assert len(rounds)==386
moves=[key(c) for c in rounds if c['shadow']!=now[key(c)]['shadow']]
assert not moves,moves
black=[]
for c in cells:
    profile,scene,renderer=key(c)
    if '27.0' not in profile or renderer!='webgpu':continue
    if r.ROLES[scene]=='holdout' and not a.include_holdout:continue
    if r.ROLES[scene]=='recorded':continue
    definition=r.SCENE[scene]
    if definition['state'] not in ('rest','inactive') or definition['background'] not in r.BLACK:continue
    n=r.rgb(r.FIXTURES/profile/(scene+'.png'))
    w=r.rgb(CAL/'web-captures'/profile/scene/(scene+'__webgpu.png'))
    h,width=n.shape[:2]; scale=width/320
    b=r.rgb(r.FIXTURES/'backgrounds'/f'{definition["background"]}@{scale:g}x.png')
    rect,_,span=r.geometry(scene,scale)
    integer,analytic=r.exterior_masks(width,h,rect,scale)
    reading=r.black_read(n,w,b,integer)
    if not reading['backdropBlack']:continue
    black.append(dict(profile=profile,scene=scene,role=r.ROLES[scene],span=span,
                       pose=definition['state'],background=definition['background'],
                       integer=reading,analytic=r.black_read(n,w,b,analytic)))
result=dict(claims='c9a §5.172',withHoldout=a.include_holdout,roundReproduced=386,
            shadowDifferences=moves,black=black,blackSummary=r.summarize_black(black))
(HERE/'canonical-verdict.json').write_text(json.dumps(result,indent=1)+'\n')
print('Canonical shadow fields equal B on 386/386 declared non-holdout rows.')
print('Black cells',len(black),'holdout',sum(x['role']=='holdout' for x in black),
      'pixels',sum(x['integer']['pixels'] for x in black))
for row in black:
    if row['integer']['aboveZero'] or row['analytic']['aboveZero']:
        print('ZERO TARGET MISSED',json.dumps(row))
