"""Declared W39 encoded boundary basis, independent of any native pixels.

`radial`'s default field is a local affine straight, used for synthetic checks.
A curved/continuous path caller must supply a field evaluator at each subpixel;
no local straight approximation is silently used for the native arc fit.
"""
import numpy as np
from body import W


def radial(d,ny,scale,width,exponent,order=8,field=None):
    d=np.asarray(d);ny=np.asarray(ny);scale=np.asarray(scale)
    nx=np.sqrt(np.maximum(1-ny*ny,0));result=np.zeros((len(d),11))
    for y in (np.arange(order)+.5)/order-.5:
      for x in (np.arange(order)+.5)/order-.5:
        if field is None:ds=d+(nx*x+ny*y)/scale;nys=ny
        else:ds,nys=field(x/scale,y/scale)
        t=-ds;even=abs(nys)**exponent;signed=np.maximum(0,-nys)**exponent
        line=np.maximum(1-t/width,0)*(t>=0)
        hats=np.stack([np.interp(t,[0,2,6,12],v,left=0,right=0)
                       for v in [[1,0,0,0],[0,1,0,0],[0,0,1,0]]],axis=1)
        result+=np.column_stack((line*even,line*signed,hats,hats*even[:,None],hats*signed[:,None]))
    return result/(order*order)

def features(body,radial):
    b=np.broadcast_to(body,(len(radial),3));y=b@W;z=b-y[:,None]
    colour=np.stack((np.ones_like(b),np.broadcast_to(y[:,None],b.shape),z,y[:,None]*z),axis=-1)
    return (radial[:,None,:,None]*colour[:,:,None,:]).reshape(len(radial),3,44)

def forward(body,radial,q):return np.clip(body+features(body,radial)@q,0,1)

def h4(body,backdrop,radial,q):
    b=np.broadcast_to(body,(len(radial),3));bb=np.broadcast_to(backdrop,b.shape)
    return radial[:,1,None]*(q[0]*(bb-(bb@W)[:,None])+q[1]*(b-(b@W)[:,None]))
