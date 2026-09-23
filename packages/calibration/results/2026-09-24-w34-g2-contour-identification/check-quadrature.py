#!/usr/bin/env python3.12
"""Check shortcuts on every distinct non-holdout circular fixed-mask geometry."""
import base64
import gzip
import json
import numpy as np
import identification as M
import fast

wave=M.W.default_wave();reader=wave.reader(M.G1/'repeat');seen=set();rows=[]
for cell,kind in sorted(reader.entries):
    if kind!='crop' or cell.split('/',1)[1] not in reader.allowed:continue
    crop=json.loads(gzip.decompress(reader.read(cell,'crop')))
    row=next(r for r in crop['runs'] if r['protocol']=='normal' and r['admitted'])
    p=M.I.unpack(base64.b64decode(crop['states'][row['state']]))
    if p['component']['kind']!='capsule-circular':continue
    key=json.dumps([p['component'],p['scale'],p['alignment']['translationDevicePx']],sort_keys=True)
    if key in seen:continue
    seen.add(key);h,w=p['rgb'].shape[:2]
    d,*_=M.I.geometry(w,h,p['component'],p['scale'],p['alignment']['translationDevicePx'])
    y,x=np.where((d>=-2)&(d<4));xy=np.c_[x,y]
    old=fast.coverage_reference(xy,p['component'],p['scale'],p['alignment']['translationDevicePx'])
    new=fast.coverage(xy,p['component'],p['scale'],p['alignment']['translationDevicePx'])
    errors={k:float(abs(old[k]-new[k]).max()) for k in old}
    for k in old:np.testing.assert_allclose(old[k],new[k],atol=1e-14,rtol=0)
    rows.append(dict(witness=cell,pixels=len(x),maximumDifferences=errors))
    print('fixed-mask quadrature agrees',len(rows),cell,flush=True)
M.save(M.HERE/'native-quadrature-check.json',dict(geometries=len(rows),rows=rows,holdout=False,
    rule='Every 64x64 body/band/angular moment agrees to absolute 1e-14; no native residual is fitted.'))
