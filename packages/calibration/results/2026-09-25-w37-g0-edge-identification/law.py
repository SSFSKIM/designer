"""W37 sibling effective boundary forward extension; not runtime code."""
import sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
W=np.array([.2126,.7152,.0722])
def features(body,d,ny,shape,space):
    if space not in ('linear','encoded'):raise ValueError('unknown family space')
    d,ny=np.broadcast_arrays(np.asarray(d,float),np.asarray(ny,float))
    body=np.broadcast_to(np.asarray(body,float),d.shape+(3,))
    inside=(d>=-6)&(d<0);t=-d
    line=np.maximum(1-t/shape['width'],0)**2*inside
    shoulder=np.maximum(1-t/shape['shoulder'],0)**2*inside
    f=((1-shape['share'])*line+shape['share']*shoulder)*abs(ny)**shape['exponent']
    y=body@W;z=body-y[...,None]
    return np.stack([np.broadcast_to(f[...,None],body.shape),
        np.broadcast_to((f*y)[...,None],body.shape),f[...,None]*z,
        (f*y)[...,None]*z,shoulder[...,None]*body],axis=-1)
def forward(body,d,ny,shape,coefficients,space,alpha=1,coverage=1):
    body=np.asarray(body,float)
    transformed=body+features(body,d,ny,shape,space)@np.asarray(coefficients,float)
    linear=edge.decode(np.clip(transformed,0,1)) if space=='encoded' else transformed
    # All appearance operators are off: the inherited helper owns the final
    # opaque encode/clamp and, crucially, refuses every non-unit alpha/coverage.
    result=edge.forward(linear,np.asarray(d),1,a=0,g=0,shadow_alpha=0,
        alpha=alpha,coverage=coverage)
    result['unclipped']=transformed
    return result
