#!/usr/bin/env python3.12
"""Qualify CSS's no-floor statement by its actual exterior mask (§5.172)."""
import importlib.util
import json
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
CAL=HERE.parent.parent
G0=CAL/'results/2026-09-22-w33-g0-rim-cut'
sys.path.insert(0,str(G0))
spec=importlib.util.spec_from_file_location('w33_css_ref',G0/'referee.py')
r=importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
readings=json.loads((HERE/'sheet-readings.json').read_text())
out=[]
for record in readings:
    if not record['cssBlack']['pixels']:continue
    profile,scene=record['profile'],record['scene']
    tree=(Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
          if record['generation']=='BEFORE' else CAL/'web-captures')
    n=r.rgb(r.FIXTURES/profile/(scene+'.png'))
    w=r.rgb(tree/profile/scene/(scene+'__css.png'))
    h,width=n.shape[:2]; scale=width/320
    b=r.rgb(r.FIXTURES/'backgrounds'/f'{r.SCENE[scene]["background"]}@{scale:g}x.png')
    rect,radius,_=r.geometry(scene,scale)
    integer,analytic=r.exterior_masks(width,h,rect,scale)
    black=np.all(n==0,axis=2)&np.all(b==0,axis=2)
    hit=integer&black&np.any(w>0,axis=2)
    d,_=r.sdf_masks(width,h,rect,radius)
    row=dict(profile=profile,scene=scene,generation=record['generation'],
             integer=r.black_read(n,w,b,integer),analytic=r.black_read(n,w,b,analytic),
             minSdfCss=float(d[hit].min()/scale) if hit.any() else None,
             maxSdfCss=float(d[hit].max()/scale) if hit.any() else None,
             maxByte=float(w[hit].max()) if hit.any() else 0,
             distanceBands={f'{lo}-{hi}':int((hit&(d/scale>=lo)&(d/scale<hi)).sum())
                            for lo,hi in [(0,2),(2,3),(3,6),(6,12),(12,1000)]})
    out.append(row)
    print(profile,scene,record['generation'],'integer',row['integer']['aboveZero'],
          'analytic',row['analytic']['aboveZero'],'sdf',row['minSdfCss'],row['maxSdfCss'],'max',row['maxByte'],row['distanceBands'])
(HERE/'css-floor.json').write_text(json.dumps(out,indent=1)+'\n')
