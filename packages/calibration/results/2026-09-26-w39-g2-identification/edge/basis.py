"""Exact supplied-path quadrature for the sealed W39 11-function geometry basis.

Samples are in CSS coordinates relative to the attested member, not registered
against its opaque control. Circular stadiums use their exact SDF; other paths
use the G0 reader's <=1/1024-CSS flattened supplied path, never circular corners.
"""
import numpy as np


def samples(shape,xy,scale,order,readers):
    x=np.asarray(xy)[:,0];y=np.asarray(xy)[:,1]
    depths=[];normals=[]
    for dy in (np.arange(order)+.5)/order-.5:
      for dx in (np.arange(order)+.5)/order-.5:
        q=np.column_stack((x+.5+dx,y+.5+dy))
        if shape.circular:
            d,nx,ny,arc=readers.I.stadium(q[:,0],q[:,1],shape.rect(scale),min(shape.size)/2*scale)
        else:d,nx,ny,arc=readers._path_field(q,shape,scale,(0,0))
        depths.append(-d/scale);normals.append(ny)
    return np.stack(depths,axis=1),np.stack(normals,axis=1)

def radial(t,ny,width,exponent):
    even=abs(ny)**exponent;signed=np.maximum(0,-ny)**exponent
    line=np.maximum(1-t/width,0)*(t>=0)
    hats=np.stack([np.interp(t,[0,2,6,12],v,left=0,right=0)
                   for v in [[1,0,0,0],[0,1,0,0],[0,0,1,0]]],axis=2)
    return np.column_stack(((line*even).mean(1),(line*signed).mean(1),
        hats.mean(1),(hats*even[:,:,None]).mean(1),(hats*signed[:,:,None]).mean(1)))
