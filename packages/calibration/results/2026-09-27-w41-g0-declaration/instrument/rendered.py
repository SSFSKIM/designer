"""Same supplied-path readers and residuals for web PNGs and native frames.

Payload admission is the caller's guarded-reader responsibility, not bypassed
by a second fixture file loader here. A capture is a complete opaque frame at
native scale, not a resized crop. This module never opens native files.
"""
from pathlib import Path
import numpy as np
from PIL import Image
import instrument as m

def resolution(a,b,bar_a,bar_b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if a.shape!=b.shape or not a.size or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):raise ValueError('matching finite admitted predictions required')
    bound=np.maximum(3,np.asarray(bar_a)+np.asarray(bar_b))
    delta=abs(a-b)
    return dict(verdict='separated instances' if np.any(delta>=bound) else 'insufficient resolution',maximumSeparationCodes=float(delta.max()),bound=np.broadcast_to(bound,delta.shape).tolist())

def rank(jacobian):
    j=np.atleast_2d(jacobian);s=np.linalg.svd(j,compute_uv=False)
    tol=max(j.shape)*np.finfo(float).eps*(s[0] if len(s) else 0)
    return dict(rank=int(np.sum(s>tol)),singularValues=s.tolist(),tolerance=float(tol))

def read_capture(path):
    im=np.asarray(Image.open(Path(path)).convert('RGBA'))
    if np.any(im[...,3]!=255):raise ValueError('capture must name complete opaque composite')
    return im[...,:3].astype(float)

def score_capture(path,payloads,baseline=None):
    if len(payloads)!=7:raise ValueError('all seven native repeats required')
    web=read_capture(path);p=payloads[0];shapes=m.readers.shapes_of(p['component']);scale=p['scale']
    if web.shape!=np.asarray(p['rgb']).shape:raise ValueError('native/web frame dimensions differ')
    for q in payloads:
        if q['component']!=p['component'] or q['scale']!=scale or np.asarray(q['rgb']).shape!=web.shape:raise ValueError('repeat geometry changed')
    geo=m.readers.geometry(web.shape[:2],shapes,scale)
    native=np.array([q['rgb'] for q in payloads],float)
    base=None if baseline is None else read_capture(baseline)
    if base is not None and base.shape!=web.shape:raise ValueError('witness baseline dimensions differ')
    deeps=[];exterior=[];interior=[];diagnostic=[]
    for member in range(len(shapes)):
        deep=m.readers.deep_body(web,geo,member)
        values=[m.readers.deep_body(q['rgb'],geo,member) for q in payloads]
        if deep['medianRGB'] is None or any(v['medianRGB'] is None for v in values):
            deeps.append(dict(member=member,status='UNMEASURED',survives=False))
        else:
            d=m.score_bin(np.array([deep['medianRGB']]),np.array([[v['medianRGB']] for v in values]),minimum=1)
            deeps.append(dict(member=member,**d))
        bins,labels=m.readers.edge_bins(geo,member)
        for i,b in enumerate(bins):
            mask=labels==i
            if b['part']=='boundary':
                diagnostic.append(dict(**b,webMean=None if not mask.any() else web[mask].mean(0).tolist()));continue
            if b['shell']>=0:
                exterior.append(dict(**b,score=m.score_bin(web[mask],native[:,mask])))
            elif b['shell'] in (-1,-2,-3):
                interior.append(dict(**b,strokeWitness='UNMEASURED' if base is None or not mask.any() else 'unchanged' if np.array_equal(web[mask],base[mask]) else 'changed',maximumChangeCodes=None if base is None or not mask.any() else float(abs(web[mask]-base[mask]).max())))
    return dict(deep=deeps,exterior=exterior,interiorWitnesses=interior,straddlingDiagnostic=diagnostic,
                scorer='same w39_readers geometry/deep and W41 absolute-before-aggregation residuals',
                nativePayloadsOpenedByScorer=0)
