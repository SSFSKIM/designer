"""Declared pixel-averaged encoded boundary law, not a runtime prototype (§5.182)."""
import numpy as np
from common import edge
W=np.array([.2126,.7152,.0722])

def stride(family):
    if family not in ('F1','F2','F3'):raise ValueError('undeclared family')
    return 6 if family=='F3' else 4

def radial(r,shape,family,order=8):
    """Integrate the kernel, with the declared held centre arc classification."""
    stride(family)
    d,nx,ny=[np.asarray(r[k],float) for k in ['d','nx','ny']]
    arc=np.asarray(r['arc']);radius=r['span']/2
    result=np.zeros((len(d),7))
    for y in (np.arange(order)+.5)/order-.5:
        for x in (np.arange(order)+.5)/order-.5:
            dx=x/r['scale'];dy=y/r['scale']
            vx=(radius+d)*nx+dx;vy=(radius+d)*ny+dy
            length=np.hypot(vx,vy)
            ds=np.where(arc,length-radius,d+nx*dx+ny*dy)
            nys=np.where(arc,vy/np.maximum(length,1e-15),ny)
            t=-ds;inside=t>=0;a=abs(nys)**shape['exponent']
            line=np.maximum(1-t/shape['width'],0)**(2 if family=='F2' else 1)*inside
            hats=[np.interp(t,[0,2,6,12],values,left=0,right=0)
                  for values in [[1,0,0,0],[0,1,0,0],[0,0,1,0]]]
            h=np.stack(hats,axis=-1)
            result+=np.concatenate([(line*a)[:,None],h,h*a[:,None]],axis=-1)
    return result/(order*order)

def features(body,radial_basis,family):
    """Each radial function has an independent luma and chroma polynomial."""
    b=np.broadcast_to(np.asarray(body,float),(len(radial_basis),3))
    y=b@W;z=b-y[:,None]
    base=[np.ones_like(b),np.broadcast_to(y[:,None],b.shape)]
    if stride(family)==6:base.append(np.broadcast_to(y[:,None]**2,b.shape))
    base.extend([z,y[:,None]*z])
    if stride(family)==6:base.append(y[:,None]**2*z)
    colour=np.stack(base,axis=-1)
    return (radial_basis[:,None,:,None]*colour[:,:,None,:]).reshape(len(b),3,-1)

def forward(body,x,coefficients,d,alpha=1,coverage=1):
    transformed=np.asarray(body)+x@np.asarray(coefficients)
    return edge.forward(edge.decode(np.clip(transformed,0,1)),d,1,a=0,g=0,
        shadow_alpha=0,alpha=alpha,coverage=coverage)['encoded']
