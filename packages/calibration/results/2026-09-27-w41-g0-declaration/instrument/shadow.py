"""Held macOS27 outer-shadow arithmetic on supplied paths, not a native fit.

The provenance is W39's runtime-resolved four documents; every referenced byte
is rechecked on load. This is continuous field arithmetic, not a claim that
texture reconstruction or the browser compositor was tested by the CPU port.
"""
import hashlib
import json
import numpy as np
import instrument as m

def materials():
    side=json.loads((m.G2/'instrument/resolved-materials.provenance.json').read_text())
    path=m.G2/'instrument/resolved-materials.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest()==side['materialsSha256']
    for row in side['sourceFiles']:
        assert hashlib.sha256((m.ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    for row in side['documents']:
        assert hashlib.sha256((m.ROOT/row['path']).read_bytes()).hexdigest()==row['fileSha256']
    return {k:v for k,v in json.loads(path.read_text()).items() if k!='default'}

def thin(l,s):
    if l<=.02:return s['thinOcclusionDark']
    if l<.06:
        t=(l-.02)/.04;t=t*t*(3-2*t)
        return s['thinOcclusionDark']+(s['thinOcclusionMid']-s['thinOcclusionDark'])*t
    if l<=.74:return s['thinOcclusionMid']
    if l>=.891:return s['thinOcclusionBright']
    return s['thinOcclusionMid']+(s['thinOcclusionBright']-s['thinOcclusionMid'])*(l-.74)/(.891-.74)

def sigma(span,s):
    return s['sigmaPx']+max(s['sigmaThinOffsetPx'],s['sigmaSlopePerSpan']*(span-s['sigmaSpanRefPx']))

def occlusion(span,mat,l):
    s=mat['outerShadow']
    t=float(m.body.smooth(mat['sizeSpanMin'],mat['sizeSpanMax'],span))
    blend=t*t*(3-2*t)
    thick=np.interp(span,[96,128,160],[s['thickOcclusionAt96'],s['thickOcclusionAt128'],s['thickOcclusionAt160']])
    regime=thin(l,s)*(1-blend)+thick*blend
    return float(np.clip(regime+s['sizeGain']*t*(1-regime),0,1))

def from_distance(distance,span,mat,l):
    s=mat['outerShadow']
    if s['liftAmplitude']!=0:raise ValueError('W41 held macOS27 shadow expects zero lift')
    occ=occlusion(span,mat,l)
    d=np.asarray(distance,float)-s['spreadPx']
    x=-d/max(sigma(span,s),1e-4)
    fall=.5*(1+np.tanh(np.clip(.7978845608028654*(x+.044715*x*x*x),-20,20)))
    return (1-(1-occ)**(1/2.4))*fall

def at(q,shape,scale,mat,group_luminance):
    """Output black alpha for any device coordinates, full DOWN-shifted geometry.

    group_luminance is the CPU-resolved encoded-mean-then-decoded statistic,
    held per cell. It is not replaced by a local pixel statistic or fitted.
    """
    q=np.asarray(q,float);dims=q.shape[:-1];p=q.reshape(-1,2).copy()
    p[:,1]-=mat['outerShadow']['offsetPx']*scale
    if shape.circular:
        d=m.readers.I.stadium(p[:,0],p[:,1],shape.rect(scale),min(shape.size)/2*scale)[0]
    else:d=m.readers._path_field(p,shape,scale,(0,0))[0]
    return from_distance(d/scale,min(shape.size),mat,group_luminance).reshape(dims)
