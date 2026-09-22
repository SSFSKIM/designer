#!/usr/bin/env python3.12
"""Capsule raster control, W33 G1a (§5.171), no capture or holdout access.

Integrate an ideal geometric annulus over an 8x8 pixel footprint. Fit only its
signed depth plus an even normal term, on flat solids. Grid ranges within .5
byte of the best score are sensitivity intervals, NOT confidence intervals.
The rrect's circular SDF is intentionally the same estimator as G0, not a
claim that it is Apple's continuous curve. No width is sealed by this reader.

Review correction beside, 2026-09-22: "Capsule raster control" is not a circular
geometry control. SwiftUI Capsule() defaults to .continuous; capsule-geometry.swift
and its output attest that path without rendering. The circular annulus grid's
recorded values mix geometry and coverage: pixel-area spread is possible, not
isolated. Capsule-vs-md does not isolate circle-vs-continuous geometry. G0's fixed
mask remains a valid shared-pixel non-regression referee, not isolated corner
colour-law accuracy. No recorded coverage values have been changed.
"""
import json
import sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from model import g0, normals, dump


def main():
    pop=json.loads((HERE/'population.json').read_text())['rows']
    out=[]
    for row in pop:
        if 'standard' not in row['profile']: continue
        if row['scene'].split('__')[0] not in ('light-solid','dark-solid'): continue
        if row['scene'].split('__')[1] not in ('rrect-md','capsule-button'): continue
        p,s=row['profile'],row['scene']
        assert g0.fitting_role(g0.ROLES[s],False)
        n=g0.rgb(g0.FIXTURES/p/(s+'.png'))
        w=g0.rgb(g0.CAPTURES/p/s/(s+'__webgpu.png'))
        h,width=n.shape[:2]; rect,radius,_=g0.geometry(s,width/320)
        d,sides=g0.sdf_masks(width,h,rect,radius)
        nx,ny=normals(width,h,rect,radius)
        arc=np.logical_or.reduce([m for k,m in sides.items() if k.startswith('corner-')])
        mask=(d>=-2)&(d<4)&arc
        yy,xx=np.where(mask)
        delta=n[mask]-w[mask]
        # Pixel area, not evenly spaced normal samples: angle-dependent box
        # coverage is present even for a perfectly isotropic circular stroke.
        subs=[]
        for oy in (np.arange(8)+.5)/8:
            for ox in (np.arange(8)+.5)/8:
                qx=np.abs(xx+ox-(rect[0]+rect[2])/2)-(rect[2]-rect[0])/2+radius
                qy=np.abs(yy+oy-(rect[1]+rect[3])/2)-(rect[3]-rect[1])/2+radius
                subs.append(np.hypot(np.maximum(qx,0),np.maximum(qy,0))+
                            np.minimum(np.maximum(qx,qy),0)-radius)
        dist=np.array(subs)
        fits=[]
        for centre in (0,.25,.5,.75,1):
            for stroke_width in (.5,.75,1,1.25,1.5):
                g=((dist>=centre-stroke_width/2)&(dist<centre+stroke_width/2)).mean(axis=0)
                for exponent in (1,2,4,8):
                    X=np.column_stack((g,g*np.abs(nx[mask])**exponent))
                    coef=np.linalg.lstsq(X,delta,rcond=None)[0]
                    error=delta-X@coef
                    fits.append(dict(centre=centre,width=stroke_width,exponent=exponent,
                        mae=float(np.abs(error).mean()),maeRGB=np.abs(error).mean(axis=0).tolist(),
                        coefficients=coef.tolist(),radial=[dict(start=k,pixels=int(((d[mask]>=k)&(d[mask]<k+1)).sum()),
                            maeRGB=np.abs(error[(d[mask]>=k)&(d[mask]<k+1)]).mean(axis=0).tolist()) for k in range(-2,4)]))
        best=min(fits,key=lambda f:f['mae']); near=[f for f in fits if f['mae']<=best['mae']+.5]
        nominal=min([f for f in fits if f['centre']==.5 and f['width']==1],key=lambda f:f['mae'])
        out.append(dict(**row,part='arcs',best=best,nominal=nominal,
            sensitivity=dict(rule='grid MAE <= best + .5 byte; not a confidence interval',
                centre=[min(f['centre'] for f in near),max(f['centre'] for f in near)],
                width=[min(f['width'] for f in near),max(f['width'] for f in near)]),
            grid=[{k:v for k,v in f.items() if k!='radial'} for f in fits]))
    dump(HERE/'coverage.json',dict(includeHoldout=False,samplesPerPixel=64,rows=out))
    for r in out:
        print(r['profile'],r['scene'],'best',r['best']['centre'],r['best']['width'],
              r['best']['exponent'],r['best']['maeRGB'],'nominal',r['nominal']['maeRGB'])


if __name__=='__main__': main()
