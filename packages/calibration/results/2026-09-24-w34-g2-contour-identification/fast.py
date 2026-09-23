#!/usr/bin/env python3.12
"""Exact full-pixel shortcuts for the finite subpixel quadrature (§5.176).

A signed distance is one-Lipschitz. If its centre is more than sqrt(.5) from
an indicator boundary, every subpixel is on the same side. Only partial pixels
need distance evaluation; this changes neither samples nor the declared model.
"""
import json
import numpy as np
import identification as M
import forward as F

coverage_reference=M.coverage
baseline_reference=F.baseline
_body_cache={}


def distances(pixels,component,scale,translation):
    origin=np.array(component['suppliedPaths'][0]['frameOrigin'])*scale+translation
    size=np.array(component['size'])*scale
    return M.I.stadium(pixels[:,0]+.5,pixels[:,1]+.5,[*origin,*(origin+size)],min(size)/2)[0]


def coverage(pixels,component,scale,translation,samples=64):
    if component['kind']!='capsule-circular':
        return coverage_reference(pixels,component,scale,translation,samples)
    d=distances(pixels,component,scale,translation)
    body=(d<0).astype(float)
    out=dict(body=body,band=np.zeros(len(pixels)),
             bodyX=body*((pixels[:,0]+.5)/(320*scale)-.5),
             bodyY=body*((pixels[:,1]+.5)/(200*scale)-.5))
    for k in M.POWERS:out['q'+str(k)]=np.zeros(len(pixels))
    partial=(d>=-np.sqrt(.5))&(d<=1+np.sqrt(.5))
    if partial.any():
        fine=coverage_reference(pixels[partial],component,scale,translation,samples)
        for key,value in fine.items():out[key][partial]=value
    return out


def baseline(record,space,translation,samples=64,cov=None):
    body=record['body']
    if 'coefficients' not in body:
        return baseline_reference(record,space,translation,samples,cov)
    key=(record.get('cell','synthetic'),space,samples,json.dumps(body,sort_keys=True),record['xy'].tobytes())
    if key not in _body_cache:
        offset=(np.arange(samples)+.5)/samples
        oy,ox=np.meshgrid(offset,offset,indexing='ij');ox=ox.ravel();oy=oy.ravel()
        beta=np.array(body['coefficients'])/255;U=np.array(body['uncertaintyRGB'])/255
        output=[[],[],[]];back=[];scale=record['scale']
        for start in range(0,len(record['xy']),64):
            xy=record['xy'][start:start+64];x=xy[:,0,None]+ox;y=xy[:,1,None]+oy
            B=beta[0]+(x[:,:,None]/(320*scale)-.5)*beta[1]+(y[:,:,None]/(200*scale)-.5)*beta[2]
            values=[np.clip(B,0,1),np.clip(B-U,0,1),np.clip(B+U,0,1)]
            D=np.broadcast_to(record['D'][start:start+64,None,:]/255,B.shape)
            if space=='linear':values=[M.decode(v) for v in values];D=M.decode(D)
            for dest,value in zip(output,values):dest.extend(value.mean(axis=1))
            back.extend(D.mean(axis=1))
        _body_cache[key]=[np.array(v) for v in output],np.array(back)
    endpoints,D=_body_cache[key]
    d=distances(record['xy'],record['component'],record['scale'],translation)
    out=[np.where((d<0)[:,None],value,D) for value in endpoints]
    partial=abs(d)<=np.sqrt(.5)
    if partial.any():
        r={**record,'xy':record['xy'][partial],'D':record['D'][partial]}
        fine=baseline_reference(r,space,translation,samples)
        for a,b in zip(out,fine):a[partial]=b
    return tuple(out)


def activate():
    M.coverage=coverage
    F.baseline=baseline


if __name__=='__main__':
    activate()
    records,_=M.extract(M.W.default_wave())
    fits=json.loads((M.HERE/'qualified-fits.json').read_text())
    F.verify(records,fits,'qualified-validation')
