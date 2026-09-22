#!/usr/bin/env python3.12
"""Locate held-out zero-target misses without fitting or changing the referee (§5.172)."""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
G0=CAL/'results/2026-09-22-w33-g0-rim-cut'; sys.path.insert(0,str(G0))
spec=importlib.util.spec_from_file_location('w33_composite_ref',G0/'referee.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
oldtree=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
verdict=json.loads((HERE/'canonical-verdict.json').read_text())
rows=[]
for cell in verdict['black']:
    if not cell['integer']['aboveZero']:continue
    profile,scene=cell['profile'],cell['scene']; scale=2
    n=r.rgb(r.FIXTURES/profile/(scene+'.png'))
    w=r.rgb(CAL/'web-captures'/profile/scene/(scene+'__webgpu.png'))
    before=r.rgb(oldtree/profile/scene/(scene+'__webgpu.png'))
    b=r.rgb(r.FIXTURES/'backgrounds'/'checkerboard@2x.png')
    rect,_,_=r.geometry(scene,scale)
    mask=r.exterior_masks(n.shape[1],n.shape[0],rect,scale)[0]
    eligible=mask&np.all(n==0,axis=2)&np.all(b==0,axis=2)
    hit=eligible&np.any(w>0,axis=2)
    geometry=r.SCENES['components'][r.SCENE[scene]['component']]
    parts={}
    for name in ('base','over'):
        c=geometry[name]; width,height=c['size']; dx,dy=c.get('offset',[0,0])
        box=[(320-width)/2+dx,(200-height)/2+dy,(320+width)/2+dx,(200+height)/2+dy]
        parts[name]=dict(boxCss=box,radius=c.get('radius',height/2))
    pixels=[]
    for y,x in zip(*np.where(hit)):
        px,py=(x+.5)/scale,(y+.5)/scale
        where={name:bool(box['boxCss'][0]<=px<box['boxCss'][2] and box['boxCss'][1]<=py<box['boxCss'][3]) for name,box in parts.items()}
        pixels.append(dict(device=[int(x),int(y)],centreCss=[px,py],native=n[y,x].tolist(),
                           before=before[y,x].tolist(),after=w[y,x].tolist(),insideBoundingBoxes=where))
    rows.append(dict(profile=profile,scene=scene,parts=parts,pixels=pixels,
                     before=r.black_read(n,before,b,mask),after=cell['integer']))
    print(json.dumps(rows[-1]))
(HERE/'holdout-composite-decomposition.json').write_text(json.dumps(rows,indent=2)+'\n')
