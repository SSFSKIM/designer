"""W41 declared exterior/strip/scoring instrument. No payload opens or fitting here.

Coordinates are device pixels for quadrature and CSS for the declared strip.
The supplied path, not an opaque registration, decides support. Pixel predictions
remain available to the scorer: signed bin averages cannot masquerade as closure.
"""
import importlib.util
from pathlib import Path
import sys
import numpy as np

HERE=Path(__file__).resolve().parent
E=HERE.parent
ROOT=E.parents[3]
G0=E.parent/'2026-09-26-w39-g0-colour-edge-bed'
G2=E.parent/'2026-09-26-w39-g2-identification'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

readers=load('w41_inherited_readers',G0/'w39_readers.py')
body=load('w41_inherited_colour',G2/'instrument/body.py')
NODES=np.array([40,56,72,88,104,128,150,255],float)

def samples(shape,xy,scale,order=16):
    """Keep each supplied-path subpixel and normal; no material averaging yet."""
    xy=np.asarray(xy,float)
    if scale not in (1,2) or order not in (16,32):raise ValueError('undeclared scale/quadrature')
    u=(np.arange(order)+.5)/order
    dy,dx=np.meshgrid(u,u,indexing='ij')
    q=xy[:,None,:]+np.c_[dx.ravel(),dy.ravel()][None,:,:]
    p=q.reshape(-1,2)
    if shape.circular:
        d,nx,ny,arc=readers.I.stadium(p[:,0],p[:,1],shape.rect(scale),min(shape.size)/2*scale)
    else:d,nx,ny,arc=readers._path_field(p,shape,scale,(0,0))
    dims=q.shape[:2]
    return dict(q=q,d=d.reshape(dims),nx=nx.reshape(dims),ny=ny.reshape(dims),
                arc=arc.reshape(dims),scale=scale,radiusCSS=min(shape.size)/2 if shape.circular else 22.)

def angular(nx,ny,beta,gamma):
    if not 0<=beta<=1 or abs(gamma)>1-beta+1e-14:raise ValueError('angular parameters outside declaration')
    # N=1-beta*ny^2+gamma*ny; its maximum is the concave vertex or an endpoint.
    y=np.clip(gamma/(2*beta),-1,1) if beta>0 else (1 if gamma>=0 else -1)
    maximum=1-beta*y*y+gamma*y
    if maximum<=0:raise ValueError('zero angular normalisation')
    return np.clip((1+beta*(np.asarray(nx)**2-1)+gamma*np.asarray(ny))/maximum,0,1)

def coverage(g,width,beta,gamma,css_width=False,rho=None):
    if not 0<=width<=2:raise ValueError('width outside declaration')
    a=angular(g['nx'],g['ny'],beta,gamma)
    if rho is not None:
        if not -22<=rho<=22:raise ValueError('curvature coefficient outside declaration')
        a=np.where(g['arc'],np.clip(a*(1+rho/g['radiusCSS']),0,1),a)
    w=width*g['scale'] if css_width else width
    return a*((g['d']>0)&(g['d']<w))

def bilinear(image,q):
    """The declared pixel-centred, edge-held no-glass reconstruction."""
    image=np.asarray(image,float);q=np.asarray(q,float)-.5
    x=np.clip(q[...,0],0,image.shape[1]-1);y=np.clip(q[...,1],0,image.shape[0]-1)
    x0=np.floor(x).astype(int);y0=np.floor(y).astype(int)
    x1=np.minimum(x0+1,image.shape[1]-1);y1=np.minimum(y0+1,image.shape[0]-1)
    tx=(x-x0)[...,None];ty=(y-y0)[...,None]
    return ((1-tx)*image[y0,x0]+tx*image[y0,x1])*(1-ty)+((1-tx)*image[y1,x0]+tx*image[y1,x1])*ty

def gamut_at_luma(colour):
    y=colour@body.W
    if np.any(y < -1e-12) or np.any(y > 1+1e-12):raise ValueError('correction luma outside gamut')
    y=np.clip(y,0,1);delta=colour-y[...,None];factor=np.ones_like(y)
    for c in range(3):
        d=delta[...,c];limit=np.ones_like(d)
        np.divide(1-y,d,out=limit,where=d>0)
        np.divide(-y,d,out=limit,where=d<0)
        factor=np.minimum(factor,limit)
    return y[...,None]+np.clip(factor,0,1)[...,None]*delta

def material(b,family,q,dark=False):
    b=np.asarray(b,float);q=np.asarray(q,float)
    if not np.all(np.isfinite(b)) or not np.all(np.isfinite(q)):raise ValueError('nonfinite material input')
    if family=='M0':
        if len(q)!=2 or not 0<=q[0]<=3 or not -255<=q[1]<=255:raise ValueError('M0 bounds')
        return np.clip(q[0]*b+q[1],0,255)
    if family not in ('M1','M2'):raise ValueError('unknown material family')
    n=10 if family=='M2' and dark else 8
    if len(q)!=n or np.any(q[:8]<0) or np.any(q[:8]>255) or np.any(np.diff(q[:8])<0):raise ValueError('M1 monotone ordinate bounds')
    s=255*body.curve(b/255,NODES/255,q[:8]/255)
    if family=='M2' and dark:
        k,y0=q[8:]
        if not 0<=k<=16 or not 0<=y0<=1:raise ValueError('M2 bounds')
        linear=body.decode(b/255);y=linear@body.W
        colour=body.decode(s/255)-k*np.maximum(y-y0,0)[...,None]*(y[...,None]-linear)
        s=255*body.encode(gamut_at_luma(colour))
    return s

def composite(g,b,shadow,width,beta,gamma,family,q,dark=False,css_width=False,rho=None):
    c=coverage(g,width,beta,gamma,css_width,rho)[...,None]
    b=np.asarray(b,float);shadow=np.asarray(shadow,float)
    return ((1-c)*shadow+c*material(b,family,q,dark)).mean(axis=1)

def gradient_strip(runs,references,shape,scale):
    """No mask adaptation: row medians on the same fixed strip at both scales."""
    runs=np.asarray(runs,float);references=np.asarray(references,float)
    if runs.shape!=references.shape or runs.ndim!=4 or runs.shape[0]!=7 or runs.shape[-1]!=3:raise ValueError('seven matching RGB/reference frames required')
    if not shape.circular or tuple(shape.size)!=(120.,44.) or scale not in (1,2):raise ValueError('strip needs declared circular120x44 at 1x/2x')
    x0,y0,x1,y1=shape.rect(scale);xc=(x0+x1)/2;yc=(y0+y1)/2
    yy=np.arange(runs.shape[1])+.5;xx=np.arange(runs.shape[2])+.5
    cols=np.flatnonzero(abs(xx-xc)<=24*scale)
    rows=np.flatnonzero((yy>=y0+6*scale)&(yy<=y1-6*scale))
    if len(cols)!=48*scale or len(rows)!=32*scale:raise ValueError('incomplete fixed strip')
    rr=runs[:,rows][:,:,cols];bb=references[:,rows][:,:,cols]
    vals=np.median(rr,axis=2);refs=np.median(bb,axis=2)
    med=np.median(vals,axis=0);ref=np.median(refs,axis=0)
    if np.any(ref<121) or np.any(ref>135):raise ValueError('reference outside declared 121..135 domain')
    return dict(yCSS=((yy[rows]-yc)/scale).tolist(),depthCSS=(np.minimum(yy[rows]-y0,y1-yy[rows])/scale).tolist(),
                pixelsPerRow=len(cols),native=med.tolist(),reference=ref.tolist(),runs=vals.tolist(),
                referenceRuns=refs.tolist(),bar=(.5+.5*np.ptp(vals,axis=0)).tolist(),
                memoRowMean=np.median(rr.mean(2),axis=0).tolist(),memoReferenceMean=np.median(bb.mean(2),axis=0).tolist(),
                groupReferenceMean=references.mean(axis=(1,2)).tolist())

def score_bin(prediction,runs,minimum=4):
    """Required exterior bin; keep mixed censor status and all seven repeats.

    The bar is computed from run means, as inherited, but prediction errors are
    absolute before the spatial mean. Rail deficits remain explicit constraints.
    Only a completely uncensored cell can claim held-out coverage.
    """
    p=np.asarray(prediction,float);runs=np.asarray(runs,float)
    if runs.shape!=(7,*p.shape) or p.ndim!=2 or p.shape[1]!=3 or not np.all(np.isfinite(p)) or not np.all(np.isfinite(runs)):raise ValueError('finite pixels and seven matching repeats required')
    n=len(p);bar=.5+.5*np.ptp(runs.mean(1),axis=0) if n else np.full(3,.5)
    def score(t):
        low=t<=5;high=t>=250;censored=low|high
        errors=np.where(low,np.maximum(p-5,0),np.where(high,np.maximum(250-p,0),abs(p-t)))
        status=[];failed=[];error=[];bound_failure=[]
        for c in range(3):
            exact=~censored[:,c];rail=censored[:,c]
            fail_rail=bool(np.any(errors[rail,c]>1e-10))
            # Retain uncensored samples even when another pixel in this channel
            # is censored: their failure is binding, not erased by aggregate status.
            e=float(errors[exact,c].mean()) if np.any(exact) else None
            fail_exact=e is not None and e>max(1,float(bar[c]))
            status.append('UNMEASURED' if n<minimum or fail_rail else 'censored-bound-satisfied' if np.any(rail) else 'measured')
            failed.append(bool(fail_rail or fail_exact));error.append(e);bound_failure.append(fail_rail)
        return dict(status=status,errorCodes=error,failed=failed,boundFailure=bound_failure,
                    railPixels=censored.sum(0).tolist(),uncensoredPixels=(~censored).sum(0).tolist())
    median=score(np.median(runs,axis=0));scores=[score(r) for r in runs]
    fails=[s['failed'] for s in [median,*scores]]
    return dict(pixels=n,barRGB=bar.tolist(),median=median,runs=scores,
                survives=n>=minimum and not any(any(f) for f in fails),
                heldoutCoverage=n>=minimum and all(s=='measured' for r in [median,*scores] for s in r['status']),
                worstChannelFailure=any(any(f) for f in fails),allChannelFailure=any(all(f) for f in fails))
